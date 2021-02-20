import os 
from dotenv import load_dotenv 
from bson.objectid import ObjectId

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
# enable sessions

# App Secret
secret_key = os.getenv('SECRET_KEY')

# MongoClient
mongo_key = os.getenv('MONGO_KEY')

# Azure
azure_key = os.getenv('AZURE_KEY1')

