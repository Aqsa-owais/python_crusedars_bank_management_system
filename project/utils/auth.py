import json
import os
from typing import Optional, Dict, Any
from models.user import User
from utils.data_manager import DataManager

class AuthManager:
    """Authentication and user management"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.users = self.data_manager.load_users()
        
        # Create default admin user if no users exist
        if not self.users:
            self.create_default_admin()
    
    def create_default_admin(self):
        """Create default admin user"""
        admin_user = User.create_user(
            username="admin",
            password="admin123",
            email="admin@bank.com",
            phone="1234567890",
            role="admin"
        )
        self.users[admin_user.user_id] = admin_user
        self.data_manager.save_users(self.users)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        for user in self.users.values():
            if user.username == username and user.verify_password(password) and user.is_active:
                user.update_last_login()
                self.data_manager.save_users(self.users)
                return user
        return None
    
    def register_user(self, username: str, password: str, email: str, phone: str, role: str = "customer") -> bool:
        """Register a new user"""
        # Check if username already exists
        for user in self.users.values():
            if user.username == username:
                return False
        
        # Create new user
        new_user = User.create_user(username, password, email, phone, role)
        self.users[new_user.user_id] = new_user
        self.data_manager.save_users(self.users)
        return True
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user information"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self.data_manager.save_users(self.users)
        return True
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        user.is_active = False
        self.data_manager.save_users(self.users)
        return True
    
    def get_all_users(self) -> Dict[str, User]:
        """Get all users (for admin)"""
        return self.users
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.get_user(user_id)
        if not user or not user.verify_password(old_password):
            return False
        
        user.password_hash = User.hash_password(new_password)
        self.data_manager.save_users(self.users)
        return True