
# Recommendation System Assignment

## Overview
This project is a simple recommendation system consisting of two microservices: `generator_service` and `invoker_service`, orchestrated using Docker Compose. The system generates recommendations based on different models and caches the results using both a local cache and Redis.

The microservices are the following:
- **Generator Service**: Generates random recommendations based on a given model.
- **Invoker Service**: Manages recommendation requests, checks local and Redis caches, and triggers the generator service to create new recommendations when necessary.

## Prerequisites
Before you begin, ensure you have the following installed:
- **Docker**
- **Docker Compose**

## Project Structure
The project is organized as follows:

```
recommendation-system-docker/
│
├── generator_service/
│   ├── app.py                # Flask application for the generator service
│   ├── Dockerfile            # Dockerfile to containerize the generator service
│   └── requirements.txt      # Python dependencies for the generator service
│
├── invoker_service/
│   ├── app.py                # Flask application for the invoker service
│   ├── Dockerfile            # Dockerfile to containerize the invoker service
│   ├── .env                  # Environment variables for Redis configuration
│   └── requirements.txt      # Python dependencies for the invoker service
│
└── docker-compose.yml        # Docker Compose file to orchestrate the services
```

The `.env` file in the `invoker_service` directory contains necessary variables to connect to the Redis instance


## Installation and Setup

Follow these steps to set up and run the project:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/HakHakobyan/recommendation-system-docker.git
   cd recommendation-system-docker
   ```

2. **Build the Docker Images**:
   Build the Docker images for both services:
   ```bash
   docker-compose build
   ```

3. **Start the Services**:
   Start the services using Docker Compose:
   ```bash
   docker-compose up
   ```

   This command will start the following services:
   - `generator-service`: Running on `http://localhost:5000`
   - `invoker-service`: Running on `http://localhost:5001`

## Usage

You can interact with the services using `curl` or any API testing tool like Postman.

### 1. **Generator Service**:
   The generator service generates a random number based on the provided model name and viewer ID.

   - **Endpoint**: `http://localhost:5000/generate`
   - **Method**: `POST`
   - **Request Payload**:
     ```json
     {
       "model_name": "ModelA",
       "viewer_id": "testuser"
     }
     ```
   - **Example Command**:
     ```bash
     curl -X POST http://localhost:5000/generate -H "Content-Type: application/json" -d '{"model_name": "ModelA", "viewer_id": "testuser"}'
     ```

### 2. **Invoker Service**:
   The invoker service checks the cache for a given viewer ID. If no cached data is found, it triggers the `runcascade` function to generate recommendations.

   - **Endpoint**: `http://localhost:5001/recommend`
   - **Method**: `GET`
   - **Query Parameters**: `viewer_id` (required)
   - **Example Command**:
     ```bash
     curl "http://localhost:5001/recommend?viewer_id=testuser"
     ```

   This command checks the cache and either retrieves the cached data or triggers the generator service to create new recommendations.

## Testing

You can test the functionality by using the `curl` commands provided in the Usage section. The invoker service will interact with the generator service and store the results in both the local cache and Redis.

### Example Testing Workflow:

1. **Add a new viewer ID** (not in the cache):
   ```bash
   curl "http://localhost:5001/recommend?viewer_id=newuserId"
   ```

2. **Check if the data is cached** (same viewer ID):
   ```bash
   curl "http://localhost:5001/recommend?viewer_id=newuserId"
   ```

   The second request should retrieve the data from the cache.

 
Please note, that in the logs you can see the cases when the program gets the data from the local cache and when from Redis.

### Personal Info
Hakob Hakobyan, 
Armenia, Yereavn,
+37477641017