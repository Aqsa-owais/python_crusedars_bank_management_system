import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any
from models.bank_system import BankSystem
from models.account import Account
from models.transaction import TransactionType, TransactionStatus
from utils.auth import AuthManager
from components.analytics import Analytics

class AdminPanel:
    """Admin panel for bank management"""
    
    def __init__(self, bank_system: BankSystem, auth_manager: AuthManager):
        self.bank_system = bank_system
        self.auth_manager = auth_manager
        self.analytics = Analytics(bank_system)
    
    def display(self):
        """Display admin panel"""
        st.markdown('<div class="main-header">Admin Panel</div>', unsafe_allow_html=True)
        
        # Sidebar menu
        with st.sidebar:
            st.subheader("Admin Menu")
            menu_option = st.selectbox(
                "Select Option",
                ["Dashboard", "User Management", "Account Management", "Transaction History", "Analytics", "System Settings"]
            )
        
        # Display selected panel
        if menu_option == "Dashboard":
            self.display_dashboard()
        elif menu_option == "User Management":
            self.display_user_management()
        elif menu_option == "Account Management":
            self.display_account_management()
        elif menu_option == "Transaction History":
            self.display_transaction_history()
        elif menu_option == "Analytics":
            self.display_analytics()
        elif menu_option == "System Settings":
            self.display_system_settings()
    
    def display_dashboard(self):
        """Display admin dashboard"""
        st.subheader("System Overview")
        
        # Get system statistics
        stats = self.bank_system.get_system_stats()
        transaction_summary = self.bank_system.get_transaction_summary(30)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", stats['total_users'])
        
        with col2:
            st.metric("Total Accounts", stats['total_accounts'])
        
        with col3:
            st.metric("Total Balance", f"{stats['total_balance']:,.2f}")
        
        with col4:
            st.metric("Total Transactions", stats['total_transactions'])
        
        # Transaction summary
        st.subheader("Last 30 Days Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Deposits", f"{transaction_summary['total_deposits']:,.2f}")
        
        with col2:
            st.metric("Total Withdrawals", f"{transaction_summary['total_withdrawals']:,.2f}")
        
        with col3:
            st.metric("Total Transfers", f"{transaction_summary['total_transfers']:,.2f}")
        
        # Recent transactions
        st.subheader("Recent Transactions")
        recent_transactions = self.bank_system.get_all_transactions(20)
        
        if recent_transactions:
            df = pd.DataFrame([
                {
                    'Date': tx.created_at.strftime('%Y-%m-%d %H:%M'),
                    'Type': tx.transaction_type.value.title(),
                    'Amount': f"{tx.amount:,.2f}",
                    'Status': tx.status.value.title(),
                    'Reference': tx.reference_number
                }
                for tx in recent_transactions
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No transactions found")
    
    def display_user_management(self):
        """Display user management panel"""
        st.subheader("User Management")
        
        # Get all users
        users = self.auth_manager.get_all_users()
        
        if users:
            # Display users table
            user_data = []
            for user in users.values():
                user_data.append({
                    'Username': user.username,
                    'Email': user.email,
                    'Phone': user.phone,
                    'Role': user.role.title(),
                    'Created': user.created_at.strftime('%Y-%m-%d') if user.created_at else 'N/A',
                    'Last Login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never',
                    'Status': 'Active' if user.is_active else 'Inactive'
                })
            
            df = pd.DataFrame(user_data)
            st.dataframe(df, use_container_width=True)
            
            # User statistics
            st.subheader("User Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_users = len(users)
                st.metric("Total Users", total_users)
            
            with col2:
                admin_users = len([u for u in users.values() if u.role == 'admin'])
                st.metric("Admin Users", admin_users)
            
            with col3:
                customer_users = len([u for u in users.values() if u.role == 'customer'])
                st.metric("Customer Users", customer_users)
        else:
            st.info("No users found")
    
    def display_account_management(self):
        """Display account management panel"""
        st.subheader("Account Management")
        
        # Get all accounts
        accounts = self.bank_system.accounts
        
        if accounts:
            # Display accounts table
            account_data = []
            for account in accounts.values():
                if account.is_active:
                    user = self.auth_manager.get_user(account.user_id)
                    account_data.append({
                        'Account Number': account.account_number,
                        'Owner': user.username if user else 'Unknown',
                        'Type': account.account_type.title(),
                        'Balance': f"{account.balance:,.2f}",
                        'Created': account.created_at.strftime('%Y-%m-%d') if account.created_at else 'N/A',
                        'Status': 'Active' if account.is_active else 'Inactive'
                    })
            
            df = pd.DataFrame(account_data)
            st.dataframe(df, use_container_width=True)
            
            # Account statistics
            st.subheader("Account Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_accounts = len([a for a in accounts.values() if a.is_active])
                st.metric("Total Accounts", total_accounts)
            
            with col2:
                total_balance = sum(a.balance for a in accounts.values() if a.is_active)
                st.metric("Total Balance", f"{total_balance:,.2f}")
            
            with col3:
                avg_balance = total_balance / total_accounts if total_accounts > 0 else 0
                st.metric("Average Balance", f"{avg_balance:,.2f}")
        else:
            st.info("No accounts found")
    
    def display_transaction_history(self):
        """Display transaction history"""
        st.subheader("Transaction History")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            days_filter = st.selectbox("Time Period", [7, 30, 90, 365], index=1)
        
        with col2:
            type_filter = st.selectbox("Transaction Type", ["All", "Deposit", "Withdrawal", "Transfer"])
        
        with col3:
            status_filter = st.selectbox("Status", ["All", "Completed", "Pending", "Failed"])
        
        # Get transactions
        all_transactions = self.bank_system.get_all_transactions(1000)
        
        # Apply filters
        filtered_transactions = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_filter)
        
        for tx in all_transactions:
            if tx.created_at < start_date:
                continue
                
            if type_filter != "All" and tx.transaction_type.value != type_filter.lower():
                continue
                
            if status_filter != "All" and tx.status.value != status_filter.lower():
                continue
                
            filtered_transactions.append(tx)
        
        # Display results
        if filtered_transactions:
            transaction_data = []
            for tx in filtered_transactions:
                account = self.bank_system.get_account_by_id(tx.account_id)
                user = self.auth_manager.get_user(account.user_id) if account else None
                
                transaction_data.append({
                    'Date': tx.created_at.strftime('%Y-%m-%d %H:%M'),
                    'Reference': tx.reference_number,
                    'User': user.username if user else 'Unknown',
                    'Account': account.account_number if account else 'Unknown',
                    'Type': tx.transaction_type.value.title(),
                    'Amount': f"{tx.amount:,.2f}",
                    'Status': tx.status.value.title(),
                    'Description': tx.description or 'N/A'
                })
            
            df = pd.DataFrame(transaction_data)
            st.dataframe(df, use_container_width=True)
            
            # Transaction summary
            st.subheader("Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_count = len(filtered_transactions)
                st.metric("Total Transactions", total_count)
            
            with col2:
                total_amount = sum(tx.amount for tx in filtered_transactions if tx.status == TransactionStatus.COMPLETED)
                st.metric("Total Amount", f"{total_amount:,.2f}")
            
            with col3:
                success_rate = len([tx for tx in filtered_transactions if tx.status == TransactionStatus.COMPLETED]) / len(filtered_transactions) * 100
                st.metric("Success Rate", f"{success_rate:.1f}%")
        else:
            st.info("No transactions found for the selected criteria")
    
    def display_analytics(self):
        """Display analytics dashboard"""
        st.subheader("Analytics Dashboard")
        self.analytics.display_analytics()
    
    def display_system_settings(self):
        """Display system settings"""
        st.subheader("System Settings")
        
        # Backup data
        st.subheader("Data Backup")
        if st.button("Create Backup"):
            try:
                backup_path = self.bank_system.data_manager.backup_data()
                st.success(f"Backup created successfully at: {backup_path}")
            except Exception as e:
                st.error(f"Backup failed: {str(e)}")
        
        # System information
        st.subheader("System Information")
        st.info("Bank Management System v1.0")
        st.info("Data storage: JSON files")
        st.info("Authentication: Local user database")