"""
Utility for MongoDB operations.
"""

from pymongo import MongoClient
from config import Config

class Database:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client["telegram_userbot"]

    def get_collection(self, name):
        """Get a MongoDB collection."""
        return self.db[name]

    def insert_document(self, collection_name, document):
        """Insert a document into a collection."""
        collection = self.get_collection(collection_name)
        collection.insert_one(document)

    def find_document(self, collection_name, query):
        """Find a document in a collection."""
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def update_document(self, collection_name, query, update_data, upsert=False):
        """Update a document in a collection."""
        collection = self.get_collection(collection_name)
        collection.update_one(query, {"$set": update_data}, upsert=upsert)

    def delete_document(self, collection_name, query):
        """Delete a document from a collection."""
        collection = self.get_collection(collection_name)
        return collection.delete_one(query)
