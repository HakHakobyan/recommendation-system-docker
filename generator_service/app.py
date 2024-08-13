from flask import Flask, request, jsonify
import random

app = Flask(__name__)


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    model_name = data.get('model_name')
    viewer_id = data.get('viewer_id')

    # Simulate recommendation generation
    random_number = random.randint(1, 100)
    result = {"reason": model_name, "result": random_number}

    return jsonify(result), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# curl -X POST http://127.0.0.1:5000/generate -H "Content-Type: application/json" -d '{"model_name": "ModelA", "viewer_id": "123"}'
