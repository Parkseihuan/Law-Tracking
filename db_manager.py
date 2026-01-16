"""
MongoDB Database Manager for Law-Tracking Application
Handles all database operations for tracked laws, snapshots, and diffs
"""

import os
import certifi
from datetime import datetime
from typing import Dict, List, Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure
import json


class DatabaseManager:
    """MongoDB database manager for law tracking data"""
    
    def __init__(self, connection_string: str = None):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string: MongoDB connection URI (defaults to env variable)
        """
        self.connection_string = connection_string or os.getenv('MONGODB_URI')
        self.client = None
        self.db = None
        self.connected = False
        
        if self.connection_string:
            self._connect()
    
    def _connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                tlsCAFile=certifi.where()
            )
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client['law_tracking']
            self.connected = True
            print("✅ MongoDB connected successfully")
            
            # Create indexes
            self._create_indexes()
            
        except ConnectionFailure as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.connected = False
        except Exception as e:
            print(f"❌ MongoDB error: {e}")
            self.connected = False
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        if not self.connected:
            return
        
        try:
            # Tracked laws indexes
            self.db.tracked_laws.create_index([("법령명", ASCENDING)], unique=True)
            self.db.tracked_laws.create_index([("마지막확인", DESCENDING)])
            
            # Snapshots indexes
            self.db.snapshots.create_index([("법령명", ASCENDING), ("저장일시", DESCENDING)])
            
            # Update history indexes
            self.db.update_history.create_index([("확인일시", DESCENDING)])
            
            # Diffs indexes
            self.db.diffs.create_index([("filename", ASCENDING)], unique=True)
            
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")
    
    def is_connected(self) -> bool:
        """Check if MongoDB is connected"""
        return self.connected
    
    # ==================== Tracked Laws Operations ====================
    
    def get_all_tracked_laws(self) -> Dict:
        """Get all tracked laws"""
        if not self.connected:
            return {}
        
        try:
            laws = {}
            for doc in self.db.tracked_laws.find():
                law_name = doc.pop('법령명')
                doc.pop('_id', None)  # Remove MongoDB _id
                laws[law_name] = doc
            return laws
        except Exception as e:
            print(f"❌ Error getting tracked laws: {e}")
            return {}
    
    def get_tracked_law(self, law_name: str) -> Optional[Dict]:
        """Get a specific tracked law"""
        if not self.connected:
            return None
        
        try:
            doc = self.db.tracked_laws.find_one({"법령명": law_name})
            if doc:
                doc.pop('_id', None)
                return doc
            return None
        except Exception as e:
            print(f"❌ Error getting law {law_name}: {e}")
            return None
    
    def save_tracked_law(self, law_name: str, law_data: Dict):
        """Save or update a tracked law"""
        if not self.connected:
            return False
        
        try:
            law_data['법령명'] = law_name
            self.db.tracked_laws.replace_one(
                {"법령명": law_name},
                law_data,
                upsert=True
            )
            return True
        except Exception as e:
            print(f"❌ Error saving law {law_name}: {e}")
            return False
    
    def delete_tracked_law(self, law_name: str):
        """Delete a tracked law"""
        if not self.connected:
            return False
        
        try:
            self.db.tracked_laws.delete_one({"법령명": law_name})
            return True
        except Exception as e:
            print(f"❌ Error deleting law {law_name}: {e}")
            return False
    
    def save_all_tracked_laws(self, laws: Dict):
        """Bulk save all tracked laws"""
        if not self.connected:
            return False
        
        try:
            operations = []
            for law_name, law_data in laws.items():
                law_data['법령명'] = law_name
                operations.append({
                    'replaceOne': {
                        'filter': {'법령명': law_name},
                        'replacement': law_data,
                        'upsert': True
                    }
                })
            
            if operations:
                self.db.tracked_laws.bulk_write(operations)
            return True
        except Exception as e:
            print(f"❌ Error bulk saving laws: {e}")
            return False
    
    # ==================== Snapshots Operations ====================
    
    def save_snapshot(self, law_name: str, law_mst_seq: str, detail: Dict):
        """Save a law snapshot"""
        if not self.connected:
            return None
        
        try:
            snapshot = {
                "법령명": law_name,
                "법령일련번호": law_mst_seq,
                "저장일시": datetime.now().isoformat(),
                "상세정보": detail
            }
            result = self.db.snapshots.insert_one(snapshot)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error saving snapshot: {e}")
            return None
    
    def get_latest_snapshot(self, law_name: str) -> Optional[Dict]:
        """Get the most recent snapshot for a law"""
        if not self.connected:
            return None
        
        try:
            doc = self.db.snapshots.find_one(
                {"법령명": law_name},
                sort=[("저장일시", DESCENDING)]
            )
            if doc:
                doc.pop('_id', None)
                return doc
            return None
        except Exception as e:
            print(f"❌ Error getting latest snapshot: {e}")
            return None
    
    # ==================== Diffs Operations ====================
    
    def save_diff(self, filename: str, content: str):
        """Save a diff HTML file"""
        if not self.connected:
            return False
        
        try:
            diff_doc = {
                "filename": filename,
                "content": content,
                "created_at": datetime.now().isoformat()
            }
            self.db.diffs.replace_one(
                {"filename": filename},
                diff_doc,
                upsert=True
            )
            return True
        except Exception as e:
            print(f"❌ Error saving diff: {e}")
            return False
    
    def get_diff(self, filename: str) -> Optional[str]:
        """Get a diff HTML file"""
        if not self.connected:
            return None
        
        try:
            doc = self.db.diffs.find_one({"filename": filename})
            if doc:
                return doc.get('content')
            return None
        except Exception as e:
            print(f"❌ Error getting diff: {e}")
            return None
    
    # ==================== Update History Operations ====================
    
    def save_update_history(self, updates: List[Dict]):
        """Save update history records"""
        if not self.connected or not updates:
            return False
        
        try:
            self.db.update_history.insert_many(updates)
            return True
        except Exception as e:
            print(f"❌ Error saving update history: {e}")
            return False
    
    def get_update_history(self, limit: int = 100) -> List[Dict]:
        """Get recent update history"""
        if not self.connected:
            return []
        
        try:
            docs = self.db.update_history.find(
                {},
                sort=[("확인일시", DESCENDING)],
                limit=limit
            )
            history = []
            for doc in docs:
                doc.pop('_id', None)
                history.append(doc)
            return history
        except Exception as e:
            print(f"❌ Error getting update history: {e}")
            return []
    
    # ==================== Utility Methods ====================
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.connected = False
            print("MongoDB connection closed")
