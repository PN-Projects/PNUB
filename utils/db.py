"""
Utility for MongoDB operations.
"""

from . import mongo_db

class Database:
    def get_collection(self, name):
        """Get a MongoDB collection."""
        return mongo_db[name]

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
        
