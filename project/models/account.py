import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal

class Account:
    """Account model for bank accounts"""
    
    def __init__(self, account_id: str, user_id: str, account_number: str, 
                 account_type: str, balance: float = 0.0, created_at: Optional[datetime] = None):
        self.account_id = account_id
        self.user_id = user_id
        self.account_number = account_number
        self.account_type = account_type  # 'savings', 'checking', 'business'
        self.balance = float(balance)
        self.created_at = created_at or datetime.now()
        self.is_active = True
        self.daily_transaction_limit = 50000.0
        self.monthly_transaction_limit = 500000.0
    
    @classmethod
    def create_account(cls, user_id: str, account_type: str, initial_balance: float = 0.0):
        """Create a new account"""
        account_id = str(uuid.uuid4())
        account_number = cls.generate_account_number()
        return cls(account_id, user_id, account_number, account_type, initial_balance)
    
    @staticmethod
    def generate_account_number() -> str:
        """Generate unique account number"""
        import random
        return str(random.randint(1000000000, 9999999999))
    
    def deposit(self, amount: float) -> bool:
        """Deposit money to account"""
        if amount <= 0:
            return False
        self.balance += amount
        return True
    
    def withdraw(self, amount: float) -> bool:
        """Withdraw money from account"""
        if amount <= 0 or amount > self.balance:
            return False
        self.balance -= amount
        return True
    
    def transfer_to(self, target_account: 'Account', amount: float) -> bool:
        """Transfer money to another account"""
        if amount <= 0 or amount > self.balance:
            return False
        
        self.balance -= amount
        target_account.balance += amount
        return True
    
    def get_balance(self) -> float:
        """Get current balance"""
        return self.balance
    
    def set_transaction_limits(self, daily_limit: float, monthly_limit: float):
        """Set transaction limits"""
        self.daily_transaction_limit = daily_limit
        self.monthly_transaction_limit = monthly_limit
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert account to dictionary for JSON serialization"""
        return {
            'account_id': self.account_id,
            'user_id': self.user_id,
            'account_number': self.account_number,
            'account_type': self.account_type,
            'balance': self.balance,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'daily_transaction_limit': self.daily_transaction_limit,
            'monthly_transaction_limit': self.monthly_transaction_limit
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create account from dictionary"""
        account = cls(
            account_id=data['account_id'],
            user_id=data['user_id'],
            account_number=data['account_number'],
            account_type=data['account_type'],
            balance=data['balance'],
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )
        account.is_active = data.get('is_active', True)
        account.daily_transaction_limit = data.get('daily_transaction_limit', 50000.0)
        account.monthly_transaction_limit = data.get('monthly_transaction_limit', 500000.0)
        return account
    
    def __str__(self):
        return f"Account(number={self.account_number}, balance={self.balance}, type={self.account_type})"