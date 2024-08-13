from flask import Flask, request, jsonify
import redis
import json
import time
from collections import OrderedDict
import concurrent.futures
import requests
import os

app = Flask(__name__)

# Local Cache Implementation
class LocalCache:
    def __init__(self, max_size=3, ttl=10):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl

    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                # Move the key to the end to mark it as recently used
                self.cache.move_to_end(key)
                return value
            else:
                # TTL expired, remove the key
                del self.cache[key]
        return None

    def set(self, key, value):
        if key in self.cache:
            # Move the key to the end to mark it as recently used
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.max_size:
            # Remove the oldest item (first item in OrderedDict)
            self.cache.popitem(last=False)
        self.cache[key] = (value, time.time())

# Initialize Local Cache
local_cache = LocalCache()


# Connect to Redis
# Initialize Redis Client using environment variables
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    username=os.getenv('REDIS_USERNAME'),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True  # To get strings back instead of bytes
)

# def generator(model_name, viewer_id):
#     random_number = random.randint(1, 100)
#     data = {"reason": model_name, "result": random_number}
#     return data

def generator_service_call(model_name, viewer_id):
    url = "http://generator-service:5000/generate"  # Use service name instead of localhost
    payload = {"model_name": model_name, "viewer_id": viewer_id}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Generator Service for {model_name}: {e}")
        return None

def runcascade(viewer_id):
    model_names = ['ModelA', 'ModelB', 'ModelC', 'ModelD', 'ModelE']

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_model = {executor.submit(generator_service_call, model_name, viewer_id): model_name for model_name in model_names}

        results = []
        for future in concurrent.futures.as_completed(future_to_model):
            model_name = future_to_model[future]
            try:
                result = future.result()
                if result:  # Ensure we only append valid, non-empty results
                    results.append({"model_name": result['reason'], "random_number": result['result']})
            except Exception as e:
                print(f"Generator call failed for {model_name}: {e}")

    return results


@app.route('/recommend', methods=['GET'])
def recommend():
    viewer_id = request.args.get('viewer_id')

    # Check in the local cache first
    cached_data = local_cache.get(viewer_id)
    if cached_data:
        print(f"Data from local cache for {viewer_id}: {cached_data}")
        return jsonify(cached_data), 200

    # Check in Redis if not found in local cache
    cached_data = redis_client.get(viewer_id)
    if cached_data:
        # Deserialize JSON string to Python list
        cached_data = json.loads(cached_data)
        if cached_data:  # Ensure cached_data is not empty
            print(f"Data from Redis cache for {viewer_id}: {cached_data}")
            # Store in local cache
            local_cache.set(viewer_id, cached_data)
            return jsonify(cached_data), 200

    # If no data found in local cache or Redis, or if data is empty, run cascade
    print(f"No data found for {viewer_id}. Running cascade...")
    results = runcascade(viewer_id)

    # Save the data in both local cache and Redis
    if results:  # Ensure results are not empty before caching
        local_cache.set(viewer_id, results)
        # Serialize the list to a JSON string before storing in Redis
        redis_client.set(viewer_id, json.dumps(results))
        print(f"Data after running cascade for {viewer_id}: {results}")
        return jsonify(results), 200
    else:
        print(f"Warning: runcascade() returned an empty list for {viewer_id}.")
        return jsonify({"error": "No data generated"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
