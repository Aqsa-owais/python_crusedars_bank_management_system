from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from models.user import User
from models.account import Account
from models.transaction import Transaction, TransactionType, TransactionStatus
from utils.data_manager import DataManager
import uuid

class BankSystem:
    """Main bank system class that manages all banking operations"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.users = self.data_manager.load_users()
        self.accounts = self.data_manager.load_accounts()
        self.transactions = self.data_manager.load_transactions()
    
    def create_account(self, user_id: str, account_type: str, initial_balance: float = 0.0) -> Optional[Account]:
        """Create a new account for a user"""
        account = Account.create_account(user_id, account_type, initial_balance)
        self.accounts[account.account_id] = account
        
        # Create initial deposit transaction if initial balance > 0
        if initial_balance > 0:
            transaction = Transaction.create_transaction(
                account.account_id, 
                TransactionType.DEPOSIT, 
                initial_balance, 
                "Initial deposit"
            )
            transaction.complete_transaction()
            self.transactions[transaction.transaction_id] = transaction
        
        self.data_manager.save_accounts(self.accounts)
        self.data_manager.save_transactions(self.transactions)
        return account
    
    def get_user_accounts(self, user_id: str) -> List[Account]:
        """Get all accounts for a user"""
        return [account for account in self.accounts.values() if account.user_id == user_id and account.is_active]
    
    def get_account_by_number(self, account_number: str) -> Optional[Account]:
        """Get account by account number"""
        for account in self.accounts.values():
            if account.account_number == account_number and account.is_active:
                return account
        return None
    
    def get_account_by_id(self, account_id: str) -> Optional[Account]:
        """Get account by account ID"""
        return self.accounts.get(account_id)
    
    def deposit(self, account_id: str, amount: float, description: str = "") -> bool:
        """Deposit money to an account"""
        account = self.get_account_by_id(account_id)
        if not account or amount <= 0:
            return False
        
        # Create transaction
        transaction = Transaction.create_transaction(
            account_id, TransactionType.DEPOSIT, amount, description
        )
        
        # Process deposit
        if account.deposit(amount):
            transaction.complete_transaction()
            self.transactions[transaction.transaction_id] = transaction
            self.data_manager.save_accounts(self.accounts)
            self.data_manager.save_transactions(self.transactions)
            return True
        else:
            transaction.fail_transaction()
            self.transactions[transaction.transaction_id] = transaction
            self.data_manager.save_transactions(self.transactions)
            return False
    
    def withdraw(self, account_id: str, amount: float, description: str = "") -> bool:
        """Withdraw money from an account"""
        account = self.get_account_by_id(account_id)
        if not account or amount <= 0:
            return False
        
        # Create transaction
        transaction = Transaction.create_transaction(
            account_id, TransactionType.WITHDRAWAL, amount, description
        )
        
        # Process withdrawal
        if account.withdraw(amount):
            transaction.complete_transaction()
            self.transactions[transaction.transaction_id] = transaction
            self.data_manager.save_accounts(self.accounts)
            self.data_manager.save_transactions(self.transactions)
            return True
        else:
            transaction.fail_transaction()
            self.transactions[transaction.transaction_id] = transaction
            self.data_manager.save_transactions(self.transactions)
            return False
    
    def transfer(self, from_account_id: str, to_account_number: str, amount: float, description: str = "") -> bool:
        """Transfer money between accounts"""
        from_account = self.get_account_by_id(from_account_id)
        to_account = self.get_account_by_number(to_account_number)
        
        if not from_account or not to_account or amount <= 0:
            return False
        
        # Create transaction
        transaction = Transaction.create_transaction(
            from_account_id, TransactionType.TRANSFER, amount, description, to_account.account_id
        )
        
        # Process transfer
        if from_account.transfer_to(to_account, amount):
            transaction.complete_transaction()
            self.transactions[transaction.transaction_id] = transaction
            
            # Create corresponding deposit transaction for target account
            deposit_transaction = Transaction.create_transaction(
                to_account.account_id, TransactionType.DEPOSIT, amount, 
                f"Transfer from {from_account.account_number}", from_account.account_id
            )
            deposit_transaction.complete_transaction()
            self.transactions[deposit_transaction.transaction_id] = deposit_transaction
            
            self.data_manager.save_accounts(self.accounts)
            self.data_manager.save_transactions(self.transactions)
            return True
        else:
            transaction.fail_transaction()
            self.transactions[transaction.transaction_id] = transaction
            self.data_manager.save_transactions(self.transactions)
            return False
    
    def get_account_transactions(self, account_id: str, limit: int = 50) -> List[Transaction]:
        """Get transactions for an account"""
        account_transactions = [
            transaction for transaction in self.transactions.values()
            if transaction.account_id == account_id
        ]
        # Sort by creation date, newest first
        account_transactions.sort(key=lambda x: x.created_at, reverse=True)
        return account_transactions[:limit]
    
    def get_all_transactions(self, limit: int = 100) -> List[Transaction]:
        """Get all transactions (for admin)"""
        all_transactions = list(self.transactions.values())
        all_transactions.sort(key=lambda x: x.created_at, reverse=True)
        return all_transactions[:limit]
    
    def get_transaction_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get transaction summary for the last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        recent_transactions = [
            transaction for transaction in self.transactions.values()
            if start_date <= transaction.created_at <= end_date
        ]
        
        total_deposits = sum(
            t.amount for t in recent_transactions 
            if t.transaction_type == TransactionType.DEPOSIT and t.status == TransactionStatus.COMPLETED
        )
        
        total_withdrawals = sum(
            t.amount for t in recent_transactions 
            if t.transaction_type == TransactionType.WITHDRAWAL and t.status == TransactionStatus.COMPLETED
        )
        
        total_transfers = sum(
            t.amount for t in recent_transactions 
            if t.transaction_type == TransactionType.TRANSFER and t.status == TransactionStatus.COMPLETED
        )
        
        return {
            'period_days': days,
            'total_transactions': len(recent_transactions),
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'total_transfers': total_transfers,
            'net_flow': total_deposits - total_withdrawals
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        total_users = len([u for u in self.users.values() if u.is_active])
        total_accounts = len([a for a in self.accounts.values() if a.is_active])
        total_balance = sum(a.balance for a in self.accounts.values() if a.is_active)
        
        return {
            'total_users': total_users,
            'total_accounts': total_accounts,
            'total_balance': total_balance,
            'total_transactions': len(self.transactions)
        }