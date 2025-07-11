import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from models.bank_system import BankSystem
from models.transaction import TransactionType, TransactionStatus

class Analytics:
    """Analytics component for data visualization"""
    
    def __init__(self, bank_system: BankSystem):
        self.bank_system = bank_system
    
    def display_analytics(self):
        """Display analytics dashboard"""
        
        # Time period selector
        period_options = {
            "Last 7 days": 7,
            "Last 30 days": 30,
            "Last 90 days": 90,
            "Last 365 days": 365
        }
        selected_period = st.selectbox("Select Time Period", list(period_options.keys()), index=1)
        days = period_options[selected_period]
        
        # Get data
        all_transactions = self.bank_system.get_all_transactions(5000)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Filter transactions by date
        filtered_transactions = [
            tx for tx in all_transactions
            if start_date <= tx.created_at <= end_date and tx.status == TransactionStatus.COMPLETED
        ]
        
        if not filtered_transactions:
            st.info("No data available for the selected period")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'date': tx.created_at.date(),
                'datetime': tx.created_at,
                'type': tx.transaction_type.value,
                'amount': tx.amount,
                'status': tx.status.value,
                'account_id': tx.account_id
            }
            for tx in filtered_transactions
        ])
        
        # Key metrics
        st.subheader("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_transactions = len(filtered_transactions)
            st.metric("Total Transactions", total_transactions)
        
        with col2:
            total_volume = df['amount'].sum()
            st.metric("Total Volume", f"{total_volume:,.2f}")
        
        with col3:
            avg_transaction = df['amount'].mean()
            st.metric("Average Transaction", f"{avg_transaction:,.2f}")
        
        with col4:
            daily_avg = total_transactions / days
            st.metric("Daily Average", f"{daily_avg:.1f}")
        
        # Transaction type distribution
        st.subheader("Transaction Type Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart for transaction count
            type_counts = df['type'].value_counts()
            fig1 = px.pie(values=type_counts.values, names=type_counts.index, 
                         title="Transaction Count by Type")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Pie chart for transaction volume
            type_volume = df.groupby('type')['amount'].sum()
            fig2 = px.pie(values=type_volume.values, names=type_volume.index, 
                         title="Transaction Volume by Type")
            st.plotly_chart(fig2, use_container_width=True)
        
        # Daily transaction trend
        st.subheader("Daily Transaction Trend")
        
        # Group by date and type
        daily_data = df.groupby(['date', 'type']).agg({
            'amount': 'sum',
            'account_id': 'count'
        }).reset_index()
        daily_data.columns = ['date', 'type', 'total_amount', 'transaction_count']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily transaction count
            fig3 = px.line(daily_data, x='date', y='transaction_count', color='type',
                          title="Daily Transaction Count")
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Daily transaction volume
            fig4 = px.line(daily_data, x='date', y='total_amount', color='type',
                          title="Daily Transaction Volume")
            st.plotly_chart(fig4, use_container_width=True)
        
        # Hourly pattern analysis
        st.subheader("Hourly Transaction Pattern")
        
        df['hour'] = df['datetime'].dt.hour
        hourly_data = df.groupby('hour').agg({
            'amount': 'sum',
            'account_id': 'count'
        }).reset_index()
        hourly_data.columns = ['hour', 'total_amount', 'transaction_count']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig5 = px.bar(hourly_data, x='hour', y='transaction_count',
                         title="Transactions by Hour of Day")
            st.plotly_chart(fig5, use_container_width=True)
        
        with col2:
            fig6 = px.bar(hourly_data, x='hour', y='total_amount',
                         title="Transaction Volume by Hour of Day")
            st.plotly_chart(fig6, use_container_width=True)
        
        # Account activity analysis
        st.subheader("Account Activity Analysis")
        
        # Top active accounts
        account_activity = df.groupby('account_id').agg({
            'amount': 'sum',
            'date': 'count'
        }).reset_index()
        account_activity.columns = ['account_id', 'total_amount', 'transaction_count']
        account_activity = account_activity.sort_values('transaction_count', ascending=False)
        
        # Get account details
        account_details = []
        for _, row in account_activity.head(10).iterrows():
            account = self.bank_system.get_account_by_id(row['account_id'])
            if account:
                account_details.append({
                    'Account Number': account.account_number,
                    'Account Type': account.account_type.title(),
                    'Transaction Count': row['transaction_count'],
                    'Total Volume': f"{row['total_amount']:,.2f}",
                    'Current Balance': f"{account.balance:,.2f}"
                })
        
        if account_details:
            st.subheader("Top 10 Active Accounts")
            df_accounts = pd.DataFrame(account_details)
            st.dataframe(df_accounts, use_container_width=True)
        
        # Transaction size distribution
        st.subheader("Transaction Size Distribution")
        
        # Define amount ranges
        def categorize_amount(amount):
            if amount < 1000:
                return "< 1,000"
            elif amount < 10000:
                return "1,000 - 10,000"
            elif amount < 50000:
                return "10,000 - 50,000"
            elif amount < 100000:
                return "50,000 - 1,00,000"
            else:
                return "> 1,00,000"
        
        df['amount_category'] = df['amount'].apply(categorize_amount)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Transaction count by amount category
            amount_counts = df['amount_category'].value_counts()
            fig7 = px.bar(x=amount_counts.index, y=amount_counts.values,
                         title="Transaction Count by Amount Range")
            st.plotly_chart(fig7, use_container_width=True)
        
        with col2:
            # Transaction volume by amount category
            amount_volume = df.groupby('amount_category')['amount'].sum()
            fig8 = px.bar(x=amount_volume.index, y=amount_volume.values,
                         title="Transaction Volume by Amount Range")
            st.plotly_chart(fig8, use_container_width=True)
        
        # Monthly trends (if enough data)
        if days >= 30:
            st.subheader("Monthly Trends")
            
            df['month'] = df['datetime'].dt.to_period('M')
            monthly_data = df.groupby(['month', 'type']).agg({
                'amount': 'sum',
                'account_id': 'count'
            }).reset_index()
            monthly_data.columns = ['month', 'type', 'total_amount', 'transaction_count']
            monthly_data['month'] = monthly_data['month'].astype(str)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig9 = px.bar(monthly_data, x='month', y='transaction_count', color='type',
                             title="Monthly Transaction Count")
                st.plotly_chart(fig9, use_container_width=True)
            
            with col2:
                fig10 = px.bar(monthly_data, x='month', y='total_amount', color='type',
                              title="Monthly Transaction Volume")
                st.plotly_chart(fig10, use_container_width=True)
        
        # Summary statistics
        st.subheader("Statistical Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Transaction Amount Statistics:**")
            st.write(f"Minimum: {df['amount'].min():,.2f}")
            st.write(f"Maximum: {df['amount'].max():,.2f}")
            st.write(f"Mean: {df['amount'].mean():,.2f}")
            st.write(f"Median: {df['amount'].median():,.2f}")
            st.write(f"Standard Deviation: {df['amount'].std():,.2f}")
        
        with col2:
            st.write("**Transaction Type Summary:**")
            for tx_type in df['type'].unique():
                count = len(df[df['type'] == tx_type])
                volume = df[df['type'] == tx_type]['amount'].sum()
                st.write(f"{tx_type.title()}: {count} transactions, {volume:,.2f}")