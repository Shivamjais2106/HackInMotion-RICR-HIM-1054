#!/usr/bin/env python3
"""
Database Manager
Utility for managing MongoDB database operations
"""

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# MongoDB connection
<<<<<<< HEAD
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/kisansathi")


class DatabaseManager:
    """Manage MongoDB operations"""

=======
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/kisansathi')

class DatabaseManager:
    """Manage MongoDB operations"""
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def __init__(self):
        """Initialize database connection"""
        try:
            self.client = MongoClient(MONGODB_URI)
<<<<<<< HEAD
            self.db = self.client["kisansathi"]
=======
            self.db = self.client['kisansathi']
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
            print("✅ Connected to MongoDB")
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            self.db = None
<<<<<<< HEAD

=======
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def get_stats(self):
        """Get database statistics"""
        if not self.db:
            return None
<<<<<<< HEAD

        stats = self.db.command("dbStats")
        return {
            "database": stats["db"],
            "collections": stats["collections"],
            "data_size_mb": stats["dataSize"] / 1024 / 1024,
            "storage_size_mb": stats["storageSize"] / 1024 / 1024,
            "indexes": stats["indexes"],
        }

=======
        
        stats = self.db.command('dbStats')
        return {
            'database': stats['db'],
            'collections': stats['collections'],
            'data_size_mb': stats['dataSize'] / 1024 / 1024,
            'storage_size_mb': stats['storageSize'] / 1024 / 1024,
            'indexes': stats['indexes']
        }
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def get_collection_stats(self, collection_name):
        """Get collection statistics"""
        if not self.db:
            return None
<<<<<<< HEAD

        collection = self.db[collection_name]
        stats = collection.aggregate([{"$collStats": {"latencyHistograms": False}}])

        return {
            "collection": collection_name,
            "count": collection.count_documents({}),
            "avg_doc_size": stats.next()["size"] / collection.count_documents({})
            if collection.count_documents({}) > 0
            else 0,
        }

    # ========== USERS OPERATIONS ==========

    def create_user(self, name, email, mobile, password, agriculture_type=""):
        """Create a new user"""
        if not self.db:
            return None

        user_doc = {
            "name": name,
            "email": email,
            "mobile": mobile,
            "password": password,
            "agriculture_type": agriculture_type,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        result = self.db["users"].insert_one(user_doc)
        return str(result.inserted_id)

=======
        
        collection = self.db[collection_name]
        stats = collection.aggregate([{'$collStats': {'latencyHistograms': False}}])
        
        return {
            'collection': collection_name,
            'count': collection.count_documents({}),
            'avg_doc_size': stats.next()['size'] / collection.count_documents({}) if collection.count_documents({}) > 0 else 0
        }
    
    # ========== USERS OPERATIONS ==========
    
    def create_user(self, name, email, mobile, password, agriculture_type=''):
        """Create a new user"""
        if not self.db:
            return None
        
        user_doc = {
            'name': name,
            'email': email,
            'mobile': mobile,
            'password': password,
            'agriculture_type': agriculture_type,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        result = self.db['users'].insert_one(user_doc)
        return str(result.inserted_id)
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def get_user(self, user_id):
        """Get user by ID"""
        if not self.db:
            return None
<<<<<<< HEAD

        return self.db["users"].find_one({"_id": ObjectId(user_id)})

=======
        
        return self.db['users'].find_one({'_id': ObjectId(user_id)})
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def get_user_by_mobile(self, mobile):
        """Get user by mobile"""
        if not self.db:
            return None
<<<<<<< HEAD

        return self.db["users"].find_one({"mobile": mobile})

=======
        
        return self.db['users'].find_one({'mobile': mobile})
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def get_all_users(self):
        """Get all users"""
        if not self.db:
            return []
<<<<<<< HEAD

        return list(self.db["users"].find({}))

=======
        
        return list(self.db['users'].find({}))
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def update_user(self, user_id, **kwargs):
        """Update user"""
        if not self.db:
            return False
<<<<<<< HEAD

        kwargs["updated_at"] = datetime.now().isoformat()
        result = self.db["users"].update_one({"_id": ObjectId(user_id)}, {"$set": kwargs})
        return result.modified_count > 0

=======
        
        kwargs['updated_at'] = datetime.now().isoformat()
        result = self.db['users'].update_one(
            {'_id': ObjectId(user_id)},
            {'$set': kwargs}
        )
        return result.modified_count > 0
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def delete_user(self, user_id):
        """Delete user"""
        if not self.db:
            return False
<<<<<<< HEAD

        result = self.db["users"].delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

=======
        
        result = self.db['users'].delete_one({'_id': ObjectId(user_id)})
        return result.deleted_count > 0
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def count_users(self):
        """Count total users"""
        if not self.db:
            return 0
<<<<<<< HEAD

        return self.db["users"].count_documents({})

    # ========== GROUPS OPERATIONS ==========

=======
        
        return self.db['users'].count_documents({})
    
    # ========== GROUPS OPERATIONS ==========
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def create_group(self, name, description, avatar, created_by):
        """Create a new group"""
        if not self.db:
            return None
<<<<<<< HEAD

        user_oid = ObjectId(created_by)
        group_doc = {
            "name": name,
            "description": description,
            "avatar": avatar,
            "members": 1,
            "member_ids": [user_oid],
            "admins": [user_oid],
            "created_by": user_oid,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "lastMessage": "Group created",
            "unread": 0,
        }

        result = self.db["groups"].insert_one(group_doc)
        return str(result.inserted_id)

=======
        
        user_oid = ObjectId(created_by)
        group_doc = {
            'name': name,
            'description': description,
            'avatar': avatar,
            'members': 1,
            'member_ids': [user_oid],
            'admins': [user_oid],
            'created_by': user_oid,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'lastMessage': 'Group created',
            'unread': 0
        }
        
        result = self.db['groups'].insert_one(group_doc)
        return str(result.inserted_id)
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def get_group(self, group_id):
        """Get group by ID"""
        if not self.db:
            return None
<<<<<<< HEAD

        return self.db["groups"].find_one({"_id": ObjectId(group_id)})

=======
        
        return self.db['groups'].find_one({'_id': ObjectId(group_id)})
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def get_all_groups(self):
        """Get all groups"""
        if not self.db:
            return []
<<<<<<< HEAD

        return list(self.db["groups"].find({}))

=======
        
        return list(self.db['groups'].find({}))
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def get_user_groups(self, user_id):
        """Get groups for user"""
        if not self.db:
            return []
<<<<<<< HEAD

        user_oid = ObjectId(user_id)
        return list(self.db["groups"].find({"member_ids": user_oid}))

=======
        
        user_oid = ObjectId(user_id)
        return list(self.db['groups'].find({'member_ids': user_oid}))
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def add_member(self, group_id, user_id):
        """Add member to group"""
        if not self.db:
            return False
<<<<<<< HEAD

        user_oid = ObjectId(user_id)
        result = self.db["groups"].update_one(
            {"_id": ObjectId(group_id)},
            {
                "$push": {"member_ids": user_oid},
                "$inc": {"members": 1},
                "$set": {"updated_at": datetime.now().isoformat()},
            },
        )
        return result.modified_count > 0

=======
        
        user_oid = ObjectId(user_id)
        result = self.db['groups'].update_one(
            {'_id': ObjectId(group_id)},
            {
                '$push': {'member_ids': user_oid},
                '$inc': {'members': 1},
                '$set': {'updated_at': datetime.now().isoformat()}
            }
        )
        return result.modified_count > 0
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def remove_member(self, group_id, user_id):
        """Remove member from group"""
        if not self.db:
            return False
<<<<<<< HEAD

        user_oid = ObjectId(user_id)
        result = self.db["groups"].update_one(
            {"_id": ObjectId(group_id)},
            {
                "$pull": {"member_ids": user_oid},
                "$inc": {"members": -1},
                "$set": {"updated_at": datetime.now().isoformat()},
            },
        )
        return result.modified_count > 0

=======
        
        user_oid = ObjectId(user_id)
        result = self.db['groups'].update_one(
            {'_id': ObjectId(group_id)},
            {
                '$pull': {'member_ids': user_oid},
                '$inc': {'members': -1},
                '$set': {'updated_at': datetime.now().isoformat()}
            }
        )
        return result.modified_count > 0
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def make_admin(self, group_id, user_id):
        """Make user admin"""
        if not self.db:
            return False
<<<<<<< HEAD

        user_oid = ObjectId(user_id)
        result = self.db["groups"].update_one(
            {"_id": ObjectId(group_id)},
            {"$push": {"admins": user_oid}, "$set": {"updated_at": datetime.now().isoformat()}},
        )
        return result.modified_count > 0

=======
        
        user_oid = ObjectId(user_id)
        result = self.db['groups'].update_one(
            {'_id': ObjectId(group_id)},
            {
                '$push': {'admins': user_oid},
                '$set': {'updated_at': datetime.now().isoformat()}
            }
        )
        return result.modified_count > 0
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def remove_admin(self, group_id, user_id):
        """Remove admin status"""
        if not self.db:
            return False
<<<<<<< HEAD

        user_oid = ObjectId(user_id)
        result = self.db["groups"].update_one(
            {"_id": ObjectId(group_id)},
            {"$pull": {"admins": user_oid}, "$set": {"updated_at": datetime.now().isoformat()}},
        )
        return result.modified_count > 0

=======
        
        user_oid = ObjectId(user_id)
        result = self.db['groups'].update_one(
            {'_id': ObjectId(group_id)},
            {
                '$pull': {'admins': user_oid},
                '$set': {'updated_at': datetime.now().isoformat()}
            }
        )
        return result.modified_count > 0
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def delete_group(self, group_id):
        """Delete group"""
        if not self.db:
            return False
<<<<<<< HEAD

        # Delete group
        self.db["groups"].delete_one({"_id": ObjectId(group_id)})

        # Delete all messages in group
        self.db["messages"].delete_many({"group_id": ObjectId(group_id)})

        return True

=======
        
        # Delete group
        self.db['groups'].delete_one({'_id': ObjectId(group_id)})
        
        # Delete all messages in group
        self.db['messages'].delete_many({'group_id': ObjectId(group_id)})
        
        return True
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def count_groups(self):
        """Count total groups"""
        if not self.db:
            return 0
<<<<<<< HEAD

        return self.db["groups"].count_documents({})

    # ========== MESSAGES OPERATIONS ==========

    def send_message(self, group_id, sender_id, text, avatar="🌾"):
        """Send message to group"""
        if not self.db:
            return None

        message_doc = {
            "group_id": ObjectId(group_id),
            "sender_id": ObjectId(sender_id),
            "text": text,
            "avatar": avatar,
            "created_at": datetime.now().isoformat(),
        }

        result = self.db["messages"].insert_one(message_doc)
        return str(result.inserted_id)

=======
        
        return self.db['groups'].count_documents({})
    
    # ========== MESSAGES OPERATIONS ==========
    
    def send_message(self, group_id, sender_id, text, avatar='🌾'):
        """Send message to group"""
        if not self.db:
            return None
        
        message_doc = {
            'group_id': ObjectId(group_id),
            'sender_id': ObjectId(sender_id),
            'text': text,
            'avatar': avatar,
            'created_at': datetime.now().isoformat()
        }
        
        result = self.db['messages'].insert_one(message_doc)
        return str(result.inserted_id)
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def get_message(self, message_id):
        """Get message by ID"""
        if not self.db:
            return None
<<<<<<< HEAD

        return self.db["messages"].find_one({"_id": ObjectId(message_id)})

=======
        
        return self.db['messages'].find_one({'_id': ObjectId(message_id)})
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def get_group_messages(self, group_id, limit=50):
        """Get messages for group"""
        if not self.db:
            return []
<<<<<<< HEAD

        return list(self.db["messages"].find({"group_id": ObjectId(group_id)}).sort("created_at", -1).limit(limit))

=======
        
        return list(self.db['messages'].find(
            {'group_id': ObjectId(group_id)}
        ).sort('created_at', -1).limit(limit))
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def delete_message(self, message_id):
        """Delete message"""
        if not self.db:
            return False
<<<<<<< HEAD

        result = self.db["messages"].delete_one({"_id": ObjectId(message_id)})
        return result.deleted_count > 0

=======
        
        result = self.db['messages'].delete_one({'_id': ObjectId(message_id)})
        return result.deleted_count > 0
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def count_messages(self, group_id=None):
        """Count messages"""
        if not self.db:
            return 0
<<<<<<< HEAD

        if group_id:
            return self.db["messages"].count_documents({"group_id": ObjectId(group_id)})
        else:
            return self.db["messages"].count_documents({})

    # ========== HISTORY OPERATIONS ==========

=======
        
        if group_id:
            return self.db['messages'].count_documents({'group_id': ObjectId(group_id)})
        else:
            return self.db['messages'].count_documents({})
    
    # ========== HISTORY OPERATIONS ==========
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def create_history(self, user_id):
        """Create conversation history"""
        if not self.db:
            return None
<<<<<<< HEAD

        history_doc = {
            "user_id": ObjectId(user_id),
            "conversation": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        result = self.db["history"].insert_one(history_doc)
        return str(result.inserted_id)

=======
        
        history_doc = {
            'user_id': ObjectId(user_id),
            'conversation': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        result = self.db['history'].insert_one(history_doc)
        return str(result.inserted_id)
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def get_history(self, user_id):
        """Get conversation history"""
        if not self.db:
            return None
<<<<<<< HEAD

        return self.db["history"].find_one({"user_id": ObjectId(user_id)})

=======
        
        return self.db['history'].find_one({'user_id': ObjectId(user_id)})
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def add_to_history(self, user_id, role, message):
        """Add message to history"""
        if not self.db:
            return False
<<<<<<< HEAD

        result = self.db["history"].update_one(
            {"user_id": ObjectId(user_id)},
            {
                "$push": {"conversation": {"role": role, "message": message, "timestamp": datetime.now().isoformat()}},
                "$set": {"updated_at": datetime.now().isoformat()},
            },
            upsert=True,
        )
        return result.modified_count > 0 or result.upserted_id is not None

=======
        
        result = self.db['history'].update_one(
            {'user_id': ObjectId(user_id)},
            {
                '$push': {
                    'conversation': {
                        'role': role,
                        'message': message,
                        'timestamp': datetime.now().isoformat()
                    }
                },
                '$set': {'updated_at': datetime.now().isoformat()}
            },
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def clear_history(self, user_id):
        """Clear conversation history"""
        if not self.db:
            return False
<<<<<<< HEAD

        result = self.db["history"].delete_one({"user_id": ObjectId(user_id)})
        return result.deleted_count > 0

    # ========== UTILITY OPERATIONS ==========

=======
        
        result = self.db['history'].delete_one({'user_id': ObjectId(user_id)})
        return result.deleted_count > 0
    
    # ========== UTILITY OPERATIONS ==========
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def clear_all_data(self):
        """Clear all data (WARNING: Destructive)"""
        if not self.db:
            return False
<<<<<<< HEAD

        self.db["users"].delete_many({})
        self.db["groups"].delete_many({})
        self.db["messages"].delete_many({})
        self.db["history"].delete_many({})
        return True

=======
        
        self.db['users'].delete_many({})
        self.db['groups'].delete_many({})
        self.db['messages'].delete_many({})
        self.db['history'].delete_many({})
        return True
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def export_collection(self, collection_name, filename):
        """Export collection to JSON"""
        if not self.db:
            return False
<<<<<<< HEAD

        try:
            collection = self.db[collection_name]
            documents = list(collection.find({}))

            # Convert ObjectId to string
            for doc in documents:
                doc["_id"] = str(doc["_id"])

            with open(filename, "w") as f:
                json.dump(documents, f, indent=2)

=======
        
        try:
            collection = self.db[collection_name]
            documents = list(collection.find({}))
            
            # Convert ObjectId to string
            for doc in documents:
                doc['_id'] = str(doc['_id'])
            
            with open(filename, 'w') as f:
                json.dump(documents, f, indent=2)
            
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
            return True
        except Exception as e:
            print(f"Error exporting: {e}")
            return False
<<<<<<< HEAD

=======
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def import_collection(self, collection_name, filename):
        """Import collection from JSON"""
        if not self.db:
            return False
<<<<<<< HEAD

        try:
            with open(filename, "r") as f:
                documents = json.load(f)

=======
        
        try:
            with open(filename, 'r') as f:
                documents = json.load(f)
            
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
            collection = self.db[collection_name]
            collection.insert_many(documents)
            return True
        except Exception as e:
            print(f"Error importing: {e}")
            return False

<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
# CLI Interface
def main():
    """Main CLI interface"""
    import sys
<<<<<<< HEAD

    manager = DatabaseManager()

=======
    
    manager = DatabaseManager()
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    if len(sys.argv) < 2:
        print("Usage: python db_manager.py <command> [args]")
        print("\nCommands:")
        print("  stats                    - Show database statistics")
        print("  users                    - Show all users")
        print("  groups                   - Show all groups")
        print("  messages <group_id>      - Show messages in group")
        print("  clear-all                - Clear all data (WARNING)")
        print("  export <collection> <file> - Export collection to JSON")
        print("  import <collection> <file> - Import collection from JSON")
        return
<<<<<<< HEAD

    command = sys.argv[1]

    if command == "stats":
        stats = manager.get_stats()
        print(json.dumps(stats, indent=2))

    elif command == "users":
        users = manager.get_all_users()
        for user in users:
            user["_id"] = str(user["_id"])
        print(json.dumps(users, indent=2))

    elif command == "groups":
        groups = manager.get_all_groups()
        for group in groups:
            group["_id"] = str(group["_id"])
            group["created_by"] = str(group["created_by"])
            group["member_ids"] = [str(m) for m in group["member_ids"]]
            group["admins"] = [str(a) for a in group["admins"]]
        print(json.dumps(groups, indent=2))

    elif command == "messages" and len(sys.argv) > 2:
        group_id = sys.argv[2]
        messages = manager.get_group_messages(group_id)
        for msg in messages:
            msg["_id"] = str(msg["_id"])
            msg["group_id"] = str(msg["group_id"])
            msg["sender_id"] = str(msg["sender_id"])
        print(json.dumps(messages, indent=2))

    elif command == "clear-all":
        confirm = input("Are you sure? This will delete all data. Type 'yes' to confirm: ")
        if confirm == "yes":
=======
    
    command = sys.argv[1]
    
    if command == 'stats':
        stats = manager.get_stats()
        print(json.dumps(stats, indent=2))
    
    elif command == 'users':
        users = manager.get_all_users()
        for user in users:
            user['_id'] = str(user['_id'])
        print(json.dumps(users, indent=2))
    
    elif command == 'groups':
        groups = manager.get_all_groups()
        for group in groups:
            group['_id'] = str(group['_id'])
            group['created_by'] = str(group['created_by'])
            group['member_ids'] = [str(m) for m in group['member_ids']]
            group['admins'] = [str(a) for a in group['admins']]
        print(json.dumps(groups, indent=2))
    
    elif command == 'messages' and len(sys.argv) > 2:
        group_id = sys.argv[2]
        messages = manager.get_group_messages(group_id)
        for msg in messages:
            msg['_id'] = str(msg['_id'])
            msg['group_id'] = str(msg['group_id'])
            msg['sender_id'] = str(msg['sender_id'])
        print(json.dumps(messages, indent=2))
    
    elif command == 'clear-all':
        confirm = input("Are you sure? This will delete all data. Type 'yes' to confirm: ")
        if confirm == 'yes':
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
            manager.clear_all_data()
            print("✅ All data cleared")
        else:
            print("❌ Cancelled")
<<<<<<< HEAD

    elif command == "export" and len(sys.argv) > 3:
=======
    
    elif command == 'export' and len(sys.argv) > 3:
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
        collection = sys.argv[2]
        filename = sys.argv[3]
        if manager.export_collection(collection, filename):
            print(f"✅ Exported {collection} to {filename}")
        else:
<<<<<<< HEAD
            print("❌ Failed to export")

    elif command == "import" and len(sys.argv) > 3:
=======
            print(f"❌ Failed to export")
    
    elif command == 'import' and len(sys.argv) > 3:
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
        collection = sys.argv[2]
        filename = sys.argv[3]
        if manager.import_collection(collection, filename):
            print(f"✅ Imported {collection} from {filename}")
        else:
<<<<<<< HEAD
            print("❌ Failed to import")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
=======
            print(f"❌ Failed to import")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    main()
