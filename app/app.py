from flask import Flask, request, render_template, jsonify
import os
import uuid
from dotenv import load_dotenv
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cosmos import CosmosClient
import base64
import json

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Azure Configuration - Loaded from environment variables
COMPUTER_VISION_KEY = os.environ.get('COMPUTER_VISION_KEY')
COMPUTER_VISION_ENDPOINT = os.environ.get('COMPUTER_VISION_ENDPOINT')
COSMOS_DB_ENDPOINT = os.environ.get('COSMOS_DB_ENDPOINT')
COSMOS_DB_KEY = os.environ.get('COSMOS_DB_KEY')
COSMOS_DB_NAME = os.environ.get('COSMOS_DB_NAME', 'image-tags')
COSMOS_CONTAINER_NAME = os.environ.get('COSMOS_CONTAINER_NAME', 'results')

# Initialize Azure Computer Vision Client
vision_client = ComputerVisionClient(
    COMPUTER_VISION_ENDPOINT,
    CognitiveServicesCredentials(COMPUTER_VISION_KEY)
)

# Initialize Cosmos DB Client
cosmos_client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)
database = cosmos_client.get_database_client(COSMOS_DB_NAME)
container = database.get_container_client(COSMOS_CONTAINER_NAME)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
        
    image_file = request.files['image']
    
    # Generate a unique image_id
    image_id = str(uuid.uuid4())
    
    # Check if we already have results for this image (simplified check using hash)
    image_data = image_file.read()
    image_hash = str(hash(image_data))
    
    # Query the database for cached results
    query = f"SELECT * FROM c WHERE c.image_hash = '{image_hash}'"
    cached_results = list(container.query_items(query=query, enable_cross_partition_query=True))
    
    # If cached result exists, return it
    if cached_results:
        return jsonify(cached_results[0]['result'])
    
    # Otherwise, analyze with Computer Vision API
    try:
        # Reset file pointer to beginning after reading for hash
        image_file.seek(0)
        
        # Analyze image
        features = ['tags', 'description', 'objects']
        analysis = vision_client.analyze_image_in_stream(image_file, visual_features=features)
        
        # Prepare results
        results = {
            'tags': [{'name': tag.name, 'confidence': tag.confidence} for tag in analysis.tags],
            'description': analysis.description.captions[0].text if analysis.description.captions else "No description available",
            'objects': [{'object': obj.object_property, 'confidence': obj.confidence} for obj in analysis.objects]
        }
        
        # Store in Cosmos DB
        container.create_item({
            'id': image_id,
            'image_hash': image_hash,
            'result': results
        })
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)