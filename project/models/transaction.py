import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    FEE = "fee"

class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Transaction:
    """Transaction model for banking operations"""
    
    def __init__(self, transaction_id: str, account_id: str, transaction_type: TransactionType,
                 amount: float, description: str = "", target_account_id: Optional[str] = None,
                 created_at: Optional[datetime] = None):
        self.transaction_id = transaction_id
        self.account_id = account_id
        self.transaction_type = transaction_type
        self.amount = float(amount)
        self.description = description
        self.target_account_id = target_account_id
        self.created_at = created_at or datetime.now()
        self.status = TransactionStatus.PENDING
        self.reference_number = self.generate_reference_number()
        self.fee = 0.0
    
    @classmethod
    def create_transaction(cls, account_id: str, transaction_type: TransactionType, 
                          amount: float, description: str = "", target_account_id: Optional[str] = None):
        """Create a new transaction"""
        transaction_id = str(uuid.uuid4())
        return cls(transaction_id, account_id, transaction_type, amount, description, target_account_id)
    
    @staticmethod
    def generate_reference_number() -> str:
        """Generate unique reference number"""
        import random
        return f"TXN{random.randint(100000, 999999)}"
    
    def complete_transaction(self):
        """Mark transaction as completed"""
        self.status = TransactionStatus.COMPLETED
    
    def fail_transaction(self):
        """Mark transaction as failed"""
        self.status = TransactionStatus.FAILED
    
    def cancel_transaction(self):
        """Mark transaction as cancelled"""
        self.status = TransactionStatus.CANCELLED
    
    def add_fee(self, fee_amount: float):
        """Add transaction fee"""
        self.fee = fee_amount
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary for JSON serialization"""
        return {
            'transaction_id': self.transaction_id,
            'account_id': self.account_id,
            'transaction_type': self.transaction_type.value,
            'amount': self.amount,
            'description': self.description,
            'target_account_id': self.target_account_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'status': self.status.value,
            'reference_number': self.reference_number,
            'fee': self.fee
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create transaction from dictionary"""
        transaction = cls(
            transaction_id=data['transaction_id'],
            account_id=data['account_id'],
            transaction_type=TransactionType(data['transaction_type']),
            amount=data['amount'],
            description=data.get('description', ''),
            target_account_id=data.get('target_account_id'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )
        transaction.status = TransactionStatus(data.get('status', 'pending'))
        transaction.reference_number = data.get('reference_number', transaction.generate_reference_number())
        transaction.fee = data.get('fee', 0.0)
        return transaction
    
    def __str__(self):
        return f"Transaction(id={self.transaction_id}, type={self.transaction_type.value}, amount={self.amount})"