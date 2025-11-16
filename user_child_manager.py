"""
User and Child ID Management System
Manages user accounts and child profiles for the voice assistant
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import uuid

class UserChildManager:
    """Manages user accounts and child profiles"""
    
    def __init__(self, data_dir: Path = Path("user_data")):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        
        self.users_file = self.data_dir / "users.json"
        self.children_file = self.data_dir / "children.json"
        self.current_user_file = self.data_dir / "current_user.json"
        self.current_child_file = self.data_dir / "current_child.json"
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files if they don't exist"""
        if not self.users_file.exists():
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
        
        if not self.children_file.exists():
            with open(self.children_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
    
    def create_user(self, name: str, email: str) -> Dict:
        """Create a new user account"""
        users = self.load_users()
        
        # Check if user already exists
        for user in users:
            if user.get('email', '').lower() == email.lower():
                return user
        
        # Create new user
        user = {
            "userId": f"user-{uuid.uuid4().hex[:12]}",
            "name": name,
            "email": email.lower(),
            "createdAt": datetime.now().isoformat(),
            "children": []
        }
        
        users.append(user)
        self.save_users(users)
        
        return user
    
    def create_child(self, userId: str, name: str, age: Optional[int] = None) -> Dict:
        """Create a new child profile for a user"""
        children = self.load_children()
        users = self.load_users()
        
        # Create child
        child = {
            "childId": f"child-{uuid.uuid4().hex[:12]}",
            "userId": userId,
            "name": name,
            "age": age,
            "createdAt": datetime.now().isoformat()
        }
        
        children.append(child)
        self.save_children(children)
        
        # Add child to user's children list
        for user in users:
            if user['userId'] == userId:
                if child['childId'] not in user['children']:
                    user['children'].append(child['childId'])
                break
        
        self.save_users(users)
        
        return child
    
    def load_users(self) -> List[Dict]:
        """Load all users"""
        if not self.users_file.exists():
            return []
        
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def load_children(self) -> List[Dict]:
        """Load all children"""
        if not self.children_file.exists():
            return []
        
        try:
            with open(self.children_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def save_users(self, users: List[Dict]):
        """Save users to file"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    
    def save_children(self, children: List[Dict]):
        """Save children to file"""
        with open(self.children_file, 'w', encoding='utf-8') as f:
            json.dump(children, f, indent=2, ensure_ascii=False)
    
    def get_user_by_id(self, userId: str) -> Optional[Dict]:
        """Get user by ID"""
        users = self.load_users()
        for user in users:
            if user.get('userId') == userId:
                return user
        return None
    
    def get_child_by_id(self, childId: str) -> Optional[Dict]:
        """Get child by ID"""
        children = self.load_children()
        for child in children:
            if child.get('childId') == childId:
                return child
        return None
    
    def get_children_for_user(self, userId: str) -> List[Dict]:
        """Get all children for a user"""
        children = self.load_children()
        return [c for c in children if c.get('userId') == userId]
    
    def set_current_user(self, userId: str):
        """Set the current active user"""
        user = self.get_user_by_id(userId)
        if user:
            with open(self.current_user_file, 'w', encoding='utf-8') as f:
                json.dump(user, f, indent=2, ensure_ascii=False)
            return user
        return None
    
    def set_current_child(self, childId: str):
        """Set the current active child"""
        child = self.get_child_by_id(childId)
        if child:
            with open(self.current_child_file, 'w', encoding='utf-8') as f:
                json.dump(child, f, indent=2, ensure_ascii=False)
            return child
        return None
    
    def get_current_user(self) -> Optional[Dict]:
        """Get the current active user"""
        if not self.current_user_file.exists():
            return None
        
        try:
            with open(self.current_user_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def get_current_child(self) -> Optional[Dict]:
        """Get the current active child"""
        if not self.current_child_file.exists():
            return None
        
        try:
            with open(self.current_child_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def ensure_default_setup(self) -> tuple:
        """Ensure there's at least one user and child, create defaults if needed"""
        current_user = self.get_current_user()
        current_child = self.get_current_child()
        
        if not current_user:
            # Create default user
            current_user = self.create_user("Default User", "user@example.com")
            self.set_current_user(current_user['userId'])
        
        if not current_child:
            # Create default child for user
            current_child = self.create_child(current_user['userId'], "Default Child")
            self.set_current_child(current_child['childId'])
        
        return current_user, current_child


