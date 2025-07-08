import hashlib
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

class User:
    """User model for authentication and user management"""
    
    def __init__(self, user_id: str, username: str, email: str, phone: str, role: str, 
                 password_hash: str, created_at: Optional[datetime] = None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.phone = phone
        self.role = role  # 'admin' or 'customer'
        self.password_hash = password_hash
        self.created_at = created_at or datetime.now()
        self.last_login = None
        self.is_active = True
    
    @classmethod
    def create_user(cls, username: str, password: str, email: str, phone: str, role: str = "customer"):
        """Create a new user with hashed password"""
        user_id = str(uuid.uuid4())
        password_hash = cls.hash_password(password)
        return cls(user_id, username, email, phone, role, password_hash)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return self.password_hash == self.hash_password(password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for JSON serialization"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'password_hash': self.password_hash,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create user from dictionary"""
        user = cls(
            user_id=data['user_id'],
            username=data['username'],
            email=data['email'],
            phone=data['phone'],
            role=data['role'],
            password_hash=data['password_hash'],
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )
        user.last_login = datetime.fromisoformat(data['last_login']) if data.get('last_login') else None
        user.is_active = data.get('is_active', True)
        return user
    
    def __str__(self):
        return f"User(id={self.user_id}, username={self.username}, role={self.role})"