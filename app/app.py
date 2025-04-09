from flask import Flask, request, render_template, jsonify
import os
import uuid
from dotenv import load_dotenv
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cosmos import CosmosClient
import base64
import json


load_dotenv()

app = Flask(__name__)


COMPUTER_VISION_KEY = os.environ.get('COMPUTER_VISION_KEY')
COMPUTER_VISION_ENDPOINT = os.environ.get('COMPUTER_VISION_ENDPOINT')
COSMOS_DB_ENDPOINT = os.environ.get('COSMOS_DB_ENDPOINT')
COSMOS_DB_KEY = os.environ.get('COSMOS_DB_KEY')
COSMOS_DB_NAME = os.environ.get('COSMOS_DB_NAME', 'image-tags')
COSMOS_CONTAINER_NAME = os.environ.get('COSMOS_CONTAINER_NAME', 'results')


vision_client = ComputerVisionClient(
    COMPUTER_VISION_ENDPOINT,
    CognitiveServicesCredentials(COMPUTER_VISION_KEY)
)


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
    
    
    image_id = str(uuid.uuid4())
    
    
    image_data = image_file.read()
    image_hash = str(hash(image_data))
    
    
    query = f"SELECT * FROM c WHERE c.image_hash = '{image_hash}'"
    cached_results = list(container.query_items(query=query, enable_cross_partition_query=True))
    
    
    if cached_results:
        return jsonify(cached_results[0]['result'])
    
    
    try:
        
        image_file.seek(0)
        
        
        features = ['tags', 'description', 'objects']
        analysis = vision_client.analyze_image_in_stream(image_file, visual_features=features)
        
        
        results = {
            'tags': [{'name': tag.name, 'confidence': tag.confidence} for tag in analysis.tags],
            'description': analysis.description.captions[0].text if analysis.description.captions else "No description available",
            'objects': [{'object': obj.object_property, 'confidence': obj.confidence} for obj in analysis.objects]
        }
        
        
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