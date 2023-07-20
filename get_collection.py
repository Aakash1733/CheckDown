import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Initialize Firebase Admin SDK and Firestore
cred = credentials.Certificate('key.json')  # Replace with the path to your service account key JSON file
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_collection_names():
    collections = db.collections()
    collection_names = [collection.id for collection in collections]
    return collection_names

# Usage example
collection_names = get_collection_names()
print(collection_names)
