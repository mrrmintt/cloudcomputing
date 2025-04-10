from flask import Flask, request, render_template, jsonify
import os
import uuid
from dotenv import load_dotenv
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import pyodbc
import json
import base64


load_dotenv()

app = Flask(__name__)


COMPUTER_VISION_KEY = os.environ.get('COMPUTER_VISION_KEY')
COMPUTER_VISION_ENDPOINT = os.environ.get('COMPUTER_VISION_ENDPOINT')
SQL_SERVER = os.environ.get('SQL_SERVER')
SQL_DATABASE = os.environ.get('SQL_DATABASE')
SQL_USERNAME = os.environ.get('SQL_USERNAME')
SQL_PASSWORD = os.environ.get('SQL_PASSWORD')


vision_client = ComputerVisionClient(
    COMPUTER_VISION_ENDPOINT,
    CognitiveServicesCredentials(COMPUTER_VISION_KEY)
)


def get_db_connection():
    connection_string = f"Driver={{ODBC Driver 17 for SQL Server}};Server={SQL_SERVER};Database={SQL_DATABASE};Uid={SQL_USERNAME};Pwd={SQL_PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    return pyodbc.connect(connection_string)


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='image_results' AND xtype='U')
    CREATE TABLE image_results (
        id VARCHAR(255) PRIMARY KEY,
        image_hash VARCHAR(255) NOT NULL,
        result NVARCHAR(MAX) NOT NULL
    )
    ''')
    conn.commit()
    conn.close()


init_db()

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
    
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT result FROM image_results WHERE image_hash = ?", (image_hash,))
    cached_result = cursor.fetchone()
    
    
    if cached_result:
        conn.close()
        return jsonify(json.loads(cached_result[0]))
    
    
    try:
        
        image_file.seek(0)
        
        
        features = ['tags', 'description', 'objects']
        analysis = vision_client.analyze_image_in_stream(image_file, visual_features=features)
        
        
        results = {
            'tags': [{'name': tag.name, 'confidence': tag.confidence} for tag in analysis.tags],
            'description': analysis.description.captions[0].text if analysis.description.captions else "No description available",
            'objects': [{'object': obj.object_property, 'confidence': obj.confidence} for obj in analysis.objects]
        }
        
        
        cursor.execute(
            "INSERT INTO image_results (id, image_hash, result) VALUES (?, ?, ?)",
            (image_id, image_hash, json.dumps(results))
        )
        conn.commit()
        conn.close()
        
        return jsonify(results)
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)