import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from models.bank_system import BankSystem
from models.account import Account
from models.transaction import TransactionType
from utils.auth import AuthManager

class CustomerPanel:
    """Customer panel for banking operations"""
    
    def __init__(self, bank_system: BankSystem, auth_manager: AuthManager, user_id: str):
        self.bank_system = bank_system
        self.auth_manager = auth_manager
        self.user_id = user_id
        self.user = auth_manager.get_user(user_id)
    
    def display(self):
        """Display customer panel"""
        st.markdown('<div class="main-header">Customer Dashboard</div>', unsafe_allow_html=True)
        
        # Sidebar menu
        with st.sidebar:
            st.subheader("Banking Menu")
            menu_option = st.selectbox(
                "Select Option",
                ["Dashboard", "Accounts", "Deposit", "Withdraw", "Transfer", "Transaction History", "Profile"]
            )
        
        # Display selected panel
        if menu_option == "Dashboard":
            self.display_dashboard()
        elif menu_option == "Accounts":
            self.display_accounts()
        elif menu_option == "Deposit":
            self.display_deposit()
        elif menu_option == "Withdraw":
            self.display_withdraw()
        elif menu_option == "Transfer":
            self.display_transfer()
        elif menu_option == "Transaction History":
            self.display_transaction_history()
        elif menu_option == "Profile":
            self.display_profile()
    
    def display_dashboard(self):
        """Display customer dashboard"""
        st.subheader(f"Welcome, {self.user.username}!")
        
        # Get user accounts
        accounts = self.bank_system.get_user_accounts(self.user_id)
        
        if accounts:
            # Account overview
            st.subheader("Account Overview")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Accounts", len(accounts))
            
            with col2:
                total_balance = sum(account.balance for account in accounts)
                st.metric("Total Balance", f"₹{total_balance:,.2f}")
            
            with col3:
                # Get recent transactions count
                recent_count = 0
                for account in accounts:
                    recent_transactions = self.bank_system.get_account_transactions(account.account_id, 10)
                    recent_count += len(recent_transactions)
                st.metric("Recent Transactions", recent_count)
            
            # Account cards
            st.subheader("Your Accounts")
            
            for account in accounts:
                with st.expander(f"Account: {account.account_number} ({account.account_type.title()})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Balance:** ₹{account.balance:,.2f}")
                        st.write(f"**Account Type:** {account.account_type.title()}")
                    
                    with col2:
                        st.write(f"**Created:** {account.created_at.strftime('%Y-%m-%d')}")
                        st.write(f"**Status:** {'Active' if account.is_active else 'Inactive'}")
                    
                    # Recent transactions for this account
                    recent_transactions = self.bank_system.get_account_transactions(account.account_id, 5)
                    if recent_transactions:
                        st.write("**Recent Transactions:**")
                        for tx in recent_transactions:
                            st.write(f"- {tx.created_at.strftime('%Y-%m-%d')} | {tx.transaction_type.value.title()} | ₹{tx.amount:,.2f}")
        else:
            st.info("No accounts found. Contact admin to create an account.")
            
            # Option to create account (admin approval required)
            st.subheader("Request New Account")
            with st.form("account_request_form"):
                account_type = st.selectbox("Account Type", ["savings", "checking", "business"])
                initial_deposit = st.number_input("Initial Deposit", min_value=0.0, value=1000.0)
                
                if st.form_submit_button("Request Account"):
                    # In a real system, this would send a request to admin
                    # For now, we'll create the account directly
                    account = self.bank_system.create_account(self.user_id, account_type, initial_deposit)
                    if account:
                        st.success(f"Account created successfully! Account Number: {account.account_number}")
                        st.rerun()
                    else:
                        st.error("Failed to create account")
    
    def display_accounts(self):
        """Display account details"""
        st.subheader("Account Details")
        
        accounts = self.bank_system.get_user_accounts(self.user_id)
        
        if accounts:
            # Account selection
            account_options = {f"{acc.account_number} ({acc.account_type.title()})": acc for acc in accounts}
            selected_account_key = st.selectbox("Select Account", list(account_options.keys()))
            selected_account = account_options[selected_account_key]
            
            # Account details
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Account Number:** {selected_account.account_number}")
                st.write(f"**Account Type:** {selected_account.account_type.title()}")
                st.write(f"**Balance:** ₹{selected_account.balance:,.2f}")
            
            with col2:
                st.write(f"**Created:** {selected_account.created_at.strftime('%Y-%m-%d')}")
                st.write(f"**Status:** {'Active' if selected_account.is_active else 'Inactive'}")
                st.write(f"**Daily Limit:** ₹{selected_account.daily_transaction_limit:,.2f}")
            
            # Transaction history for this account
            st.subheader("Transaction History")
            transactions = self.bank_system.get_account_transactions(selected_account.account_id, 50)
            
            if transactions:
                transaction_data = []
                for tx in transactions:
                    transaction_data.append({
                        'Date': tx.created_at.strftime('%Y-%m-%d %H:%M'),
                        'Type': tx.transaction_type.value.title(),
                        'Amount': f"₹{tx.amount:,.2f}",
                        'Status': tx.status.value.title(),
                        'Reference': tx.reference_number,
                        'Description': tx.description or 'N/A'
                    })
                
                df = pd.DataFrame(transaction_data)
                st.dataframe(df, use_container_width=True)
                
                # Transaction analysis
                st.subheader("Transaction Analysis")
                
                # Monthly transaction chart
                df_chart = pd.DataFrame([
                    {
                        'Date': tx.created_at.date(),
                        'Amount': tx.amount,
                        'Type': tx.transaction_type.value.title()
                    }
                    for tx in transactions
                ])
                
                if not df_chart.empty:
                    fig = px.line(df_chart, x='Date', y='Amount', color='Type', title='Transaction Trend')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No transactions found for this account")
        else:
            st.info("No accounts found")
    
    def display_deposit(self):
        """Display deposit form"""
        st.subheader("Deposit Money")
        
        accounts = self.bank_system.get_user_accounts(self.user_id)
        
        if accounts:
            with st.form("deposit_form"):
                # Account selection
                account_options = {f"{acc.account_number} ({acc.account_type.title()})": acc for acc in accounts}
                selected_account_key = st.selectbox("Select Account", list(account_options.keys()))
                selected_account = account_options[selected_account_key]
                
                # Deposit details
                amount = st.number_input("Deposit Amount", min_value=1.0, value=100.0)
                description = st.text_input("Description (Optional)", placeholder="Enter description")
                
                if st.form_submit_button("Deposit"):
                    if self.bank_system.deposit(selected_account.account_id, amount, description):
                        st.success(f"₹{amount:,.2f} deposited successfully!")
                        st.info(f"New balance: ₹{selected_account.balance:,.2f}")
                    else:
                        st.error("Deposit failed. Please try again.")
        else:
            st.info("No accounts found. Please create an account first.")
    
    def display_withdraw(self):
        """Display withdraw form"""
        st.subheader("Withdraw Money")
        
        accounts = self.bank_system.get_user_accounts(self.user_id)
        
        if accounts:
            with st.form("withdraw_form"):
                # Account selection
                account_options = {f"{acc.account_number} ({acc.account_type.title()}) - ₹{acc.balance:,.2f}": acc for acc in accounts}
                selected_account_key = st.selectbox("Select Account", list(account_options.keys()))
                selected_account = account_options[selected_account_key]
                
                # Withdraw details
                max_amount = selected_account.balance
                amount = st.number_input("Withdraw Amount", min_value=1.0, max_value=max_amount, value=min(100.0, max_amount))
                description = st.text_input("Description (Optional)", placeholder="Enter description")
                
                st.info(f"Available balance: ₹{selected_account.balance:,.2f}")
                
                if st.form_submit_button("Withdraw"):
                    if amount > selected_account.balance:
                        st.error("Insufficient balance!")
                    elif self.bank_system.withdraw(selected_account.account_id, amount, description):
                        st.success(f"₹{amount:,.2f} withdrawn successfully!")
                        st.info(f"New balance: ₹{selected_account.balance:,.2f}")
                    else:
                        st.error("Withdrawal failed. Please try again.")
        else:
            st.info("No accounts found. Please create an account first.")
    
    def display_transfer(self):
        """Display transfer form"""
        st.subheader("Transfer Money")
        
        accounts = self.bank_system.get_user_accounts(self.user_id)
        
        if accounts:
            with st.form("transfer_form"):
                # Source account selection
                account_options = {f"{acc.account_number} ({acc.account_type.title()}) - ₹{acc.balance:,.2f}": acc for acc in accounts}
                selected_account_key = st.selectbox("From Account", list(account_options.keys()))
                selected_account = account_options[selected_account_key]
                
                # Transfer details
                target_account_number = st.text_input("To Account Number", placeholder="Enter recipient account number")
                max_amount = selected_account.balance
                amount = st.number_input("Transfer Amount", min_value=1.0, max_value=max_amount, value=min(100.0, max_amount))
                description = st.text_input("Description (Optional)", placeholder="Enter description")
                
                st.info(f"Available balance: ₹{selected_account.balance:,.2f}")
                
                if st.form_submit_button("Transfer"):
                    if amount > selected_account.balance:
                        st.error("Insufficient balance!")
                    elif not target_account_number:
                        st.error("Please enter target account number!")
                    elif target_account_number == selected_account.account_number:
                        st.error("Cannot transfer to the same account!")
                    else:
                        # Check if target account exists
                        target_account = self.bank_system.get_account_by_number(target_account_number)
                        if not target_account:
                            st.error("Target account not found!")
                        elif self.bank_system.transfer(selected_account.account_id, target_account_number, amount, description):
                            st.success(f"₹{amount:,.2f} transferred successfully to {target_account_number}!")
                            st.info(f"New balance: ₹{selected_account.balance:,.2f}")
                        else:
                            st.error("Transfer failed. Please try again.")
        else:
            st.info("No accounts found. Please create an account first.")
    
    def display_transaction_history(self):
        """Display transaction history"""
        st.subheader("Transaction History")
        
        accounts = self.bank_system.get_user_accounts(self.user_id)
        
        if accounts:
            # Account selection
            account_options = {f"All Accounts": None}
            account_options.update({f"{acc.account_number} ({acc.account_type.title()})": acc for acc in accounts})
            selected_account_key = st.selectbox("Select Account", list(account_options.keys()))
            selected_account = account_options[selected_account_key]
            
            # Time period selection
            period_options = {
                "Last 7 days": 7,
                "Last 30 days": 30,
                "Last 90 days": 90,
                "Last 365 days": 365
            }
            selected_period = st.selectbox("Time Period", list(period_options.keys()))
            days = period_options[selected_period]
            
            # Get transactions
            all_transactions = []
            
            if selected_account:
                # Single account transactions
                transactions = self.bank_system.get_account_transactions(selected_account.account_id, 500)
                all_transactions.extend(transactions)
            else:
                # All accounts transactions
                for account in accounts:
                    transactions = self.bank_system.get_account_transactions(account.account_id, 500)
                    all_transactions.extend(transactions)
            
            # Filter by date
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            filtered_transactions = [
                tx for tx in all_transactions
                if start_date <= tx.created_at <= end_date
            ]
            
            # Sort by date
            filtered_transactions.sort(key=lambda x: x.created_at, reverse=True)
            
            if filtered_transactions:
                # Display transactions
                transaction_data = []
                for tx in filtered_transactions:
                    account = self.bank_system.get_account_by_id(tx.account_id)
                    transaction_data.append({
                        'Date': tx.created_at.strftime('%Y-%m-%d %H:%M'),
                        'Account': account.account_number if account else 'Unknown',
                        'Type': tx.transaction_type.value.title(),
                        'Amount': f"₹{tx.amount:,.2f}",
                        'Status': tx.status.value.title(),
                        'Reference': tx.reference_number,
                        'Description': tx.description or 'N/A'
                    })
                
                df = pd.DataFrame(transaction_data)
                st.dataframe(df, use_container_width=True)
                
                # Summary statistics
                st.subheader("Summary")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_transactions = len(filtered_transactions)
                    st.metric("Total Transactions", total_transactions)
                
                with col2:
                    total_deposits = sum(tx.amount for tx in filtered_transactions if tx.transaction_type == TransactionType.DEPOSIT)
                    st.metric("Total Deposits", f"₹{total_deposits:,.2f}")
                
                with col3:
                    total_withdrawals = sum(tx.amount for tx in filtered_transactions if tx.transaction_type == TransactionType.WITHDRAWAL)
                    st.metric("Total Withdrawals", f"₹{total_withdrawals:,.2f}")
                
                # Transaction chart
                if len(filtered_transactions) > 1:
                    st.subheader("Transaction Trend")
                    
                    # Prepare data for chart
                    chart_data = []
                    for tx in filtered_transactions:
                        chart_data.append({
                            'Date': tx.created_at.date(),
                            'Amount': tx.amount,
                            'Type': tx.transaction_type.value.title()
                        })
                    
                    df_chart = pd.DataFrame(chart_data)
                    
                    # Group by date and type
                    df_grouped = df_chart.groupby(['Date', 'Type']).sum().reset_index()
                    
                    fig = px.line(df_grouped, x='Date', y='Amount', color='Type', title='Daily Transaction Amounts')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Transaction type distribution
                    fig2 = px.pie(df_chart, values='Amount', names='Type', title='Transaction Distribution by Type')
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No transactions found for the selected period")
        else:
            st.info("No accounts found")
    
    def display_profile(self):
        """Display user profile"""
        st.subheader("User Profile")
        
        # Display current information
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Username:** {self.user.username}")
            st.write(f"**Email:** {self.user.email}")
            st.write(f"**Phone:** {self.user.phone}")
        
        with col2:
            st.write(f"**Role:** {self.user.role.title()}")
            st.write(f"**Created:** {self.user.created_at.strftime('%Y-%m-%d')}")
            st.write(f"**Last Login:** {self.user.last_login.strftime('%Y-%m-%d %H:%M') if self.user.last_login else 'N/A'}")
        
        # Change password
        st.subheader("Change Password")
        
        with st.form("change_password_form"):
            old_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Change Password"):
                if not old_password or not new_password or not confirm_password:
                    st.error("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("New passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                elif self.auth_manager.change_password(self.user_id, old_password, new_password):
                    st.success("Password changed successfully!")
                else:
                    st.error("Current password is incorrect")