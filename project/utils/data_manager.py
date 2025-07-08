import json
import os
from typing import Dict, Any
from models.user import User
from models.account import Account
from models.transaction import Transaction, TransactionType, TransactionStatus

class DataManager:
    """Handles data persistence using JSON files"""
    
    def __init__(self):
        self.data_dir = "data"
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.accounts_file = os.path.join(self.data_dir, "accounts.json")
        self.transactions_file = os.path.join(self.data_dir, "transactions.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
    
    def save_users(self, users: Dict[str, User]):
        """Save users to JSON file"""
        users_data = {user_id: user.to_dict() for user_id, user in users.items()}
        with open(self.users_file, 'w') as f:
            json.dump(users_data, f, indent=2)
    
    def load_users(self) -> Dict[str, User]:
        """Load users from JSON file"""
        if not os.path.exists(self.users_file):
            return {}
        
        try:
            with open(self.users_file, 'r') as f:
                users_data = json.load(f)
            
            users = {}
            for user_id, user_data in users_data.items():
                users[user_id] = User.from_dict(user_data)
            
            return users
        except (json.JSONDecodeError, KeyError, ValueError):
            return {}
    
    def save_accounts(self, accounts: Dict[str, Account]):
        """Save accounts to JSON file"""
        accounts_data = {account_id: account.to_dict() for account_id, account in accounts.items()}
        with open(self.accounts_file, 'w') as f:
            json.dump(accounts_data, f, indent=2)
    
    def load_accounts(self) -> Dict[str, Account]:
        """Load accounts from JSON file"""
        if not os.path.exists(self.accounts_file):
            return {}
        
        try:
            with open(self.accounts_file, 'r') as f:
                accounts_data = json.load(f)
            
            accounts = {}
            for account_id, account_data in accounts_data.items():
                accounts[account_id] = Account.from_dict(account_data)
            
            return accounts
        except (json.JSONDecodeError, KeyError, ValueError):
            return {}
    
    def save_transactions(self, transactions: Dict[str, Transaction]):
        """Save transactions to JSON file"""
        transactions_data = {tx_id: tx.to_dict() for tx_id, tx in transactions.items()}
        with open(self.transactions_file, 'w') as f:
            json.dump(transactions_data, f, indent=2)
    
    def load_transactions(self) -> Dict[str, Transaction]:
        """Load transactions from JSON file"""
        if not os.path.exists(self.transactions_file):
            return {}
        
        try:
            with open(self.transactions_file, 'r') as f:
                transactions_data = json.load(f)
            
            transactions = {}
            for tx_id, tx_data in transactions_data.items():
                transactions[tx_id] = Transaction.from_dict(tx_data)
            
            return transactions
        except (json.JSONDecodeError, KeyError, ValueError):
            return {}
    
    def backup_data(self):
        """Create backup of all data files"""
        import shutil
        from datetime import datetime
        
        backup_dir = os.path.join(self.data_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = os.path.join(backup_dir, f"backup_{timestamp}")
        os.makedirs(backup_subdir, exist_ok=True)
        
        # Copy all data files to backup directory
        for filename in [self.users_file, self.accounts_file, self.transactions_file]:
            if os.path.exists(filename):
                shutil.copy2(filename, backup_subdir)
        
        return backup_subdir