#!/usr/bin/env python3
"""
Database Initialization Script
Initializes MongoDB collections and indexes for KisanSathi
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/kisansathi')

def connect_db():
    """Connect to MongoDB"""
    try:
        client = MongoClient(MONGODB_URI)
        db = client['kisansathi']
        print("✅ Connected to MongoDB")
        return db
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None

def create_collections(db):
    """Create collections if they don't exist"""
    print("\n📦 Creating collections...")
    
    collections = ['users', 'groups', 'messages', 'history']
    
    for collection_name in collections:
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            print(f"  ✅ Created collection: {collection_name}")
        else:
            print(f"  ℹ️  Collection already exists: {collection_name}")

def create_indexes(db):
    """Create indexes for collections"""
    print("\n🔍 Creating indexes...")
    
    # Users indexes
    print("  Creating users indexes...")
    db['users'].create_index([('mobile', ASCENDING)], unique=True)
    db['users'].create_index([('email', ASCENDING)], unique=True)
    print("    ✅ Users indexes created")
    
    # Groups indexes
    print("  Creating groups indexes...")
    db['groups'].create_index([('created_by', ASCENDING)])
    db['groups'].create_index([('member_ids', ASCENDING)])
    print("    ✅ Groups indexes created")
    
    # Messages indexes
    print("  Creating messages indexes...")
    db['messages'].create_index([('group_id', ASCENDING), ('created_at', DESCENDING)])
    db['messages'].create_index([('sender_id', ASCENDING)])
    print("    ✅ Messages indexes created")
    
    # History indexes
    print("  Creating history indexes...")
    db['history'].create_index([('user_id', ASCENDING)])
    db['history'].create_index([('updated_at', DESCENDING)])
    print("    ✅ History indexes created")

def verify_collections(db):
    """Verify collections exist"""
    print("\n✔️  Verifying collections...")
    
    collections = db.list_collection_names()
    required = ['users', 'groups', 'messages', 'history']
    
    for collection in required:
        if collection in collections:
            count = db[collection].count_documents({})
            print(f"  ✅ {collection}: {count} documents")
        else:
            print(f"  ❌ {collection}: NOT FOUND")

def verify_indexes(db):
    """Verify indexes exist"""
    print("\n🔍 Verifying indexes...")
    
    # Users indexes
    users_indexes = db['users'].list_indexes()
    print(f"  Users indexes: {len(list(users_indexes))}")
    
    # Groups indexes
    groups_indexes = db['groups'].list_indexes()
    print(f"  Groups indexes: {len(list(groups_indexes))}")
    
    # Messages indexes
    messages_indexes = db['messages'].list_indexes()
    print(f"  Messages indexes: {len(list(messages_indexes))}")
    
    # History indexes
    history_indexes = db['history'].list_indexes()
    print(f"  History indexes: {len(list(history_indexes))}")

def get_database_stats(db):
    """Get database statistics"""
    print("\n📊 Database Statistics:")
    
    stats = db.command('dbStats')
    print(f"  Database: {stats['db']}")
    print(f"  Collections: {stats['collections']}")
    print(f"  Data Size: {stats['dataSize'] / 1024 / 1024:.2f} MB")
    print(f"  Storage Size: {stats['storageSize'] / 1024 / 1024:.2f} MB")
    print(f"  Indexes: {stats['indexes']}")

def print_header():
    """Print header"""
    print("\n" + "="*60)
    print("KisanSathi - Database Initialization")
    print("="*60)

def print_footer():
    """Print footer"""
    print("\n" + "="*60)
    print("✅ Database initialization complete!")
    print("="*60 + "\n")

def main():
    """Main function"""
    print_header()
    
    # Connect to database
    db = connect_db()
    if not db:
        print("❌ Failed to initialize database")
        return
    
    # Create collections
    create_collections(db)
    
    # Create indexes
    create_indexes(db)
    
    # Verify collections
    verify_collections(db)
    
    # Verify indexes
    verify_indexes(db)
    
    # Get statistics
    get_database_stats(db)
    
    print_footer()
    
    print("📝 Next steps:")
    print("  1. Start backend: python app_enhanced.py")
    print("  2. Start frontend: npm start")
    print("  3. Run tests: python test_http_methods.py")
    print()

if __name__ == '__main__':
    main()
