# Bank Management System

A comprehensive bank management system built with Streamlit, featuring admin panel, customer dashboard, and advanced analytics.

## Features

### Admin Panel
- System overview dashboard
- User management
- Account management
- Transaction monitoring
- Advanced analytics
- Data backup and system settings

### Customer Dashboard
- Account overview
- Deposit money
- Withdraw money
- Transfer funds
- Transaction history
- Profile management

### Analytics
- Transaction trends
- Account activity analysis
- Hourly and daily patterns
- Statistical summaries
- Interactive charts and graphs

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python with OOP
- **Data Storage**: JSON files
- **Analytics**: Pandas, Plotly
- **Authentication**: Local user database with password hashing

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd bank-management-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Default Login Credentials

- **Admin**: username: `admin`, password: `admin123`
- **Customer**: Register a new account through the login page

## Project Structure

```
bank-management-system/
├── app.py                 # Main application file
├── models/
│   ├── __init__.py
│   ├── user.py           # User model
│   ├── account.py        # Account model
│   ├── transaction.py    # Transaction model
│   └── bank_system.py    # Main banking system
├── components/
│   ├── __init__.py
│   ├── admin_panel.py    # Admin interface
│   ├── customer_panel.py # Customer interface
│   └── analytics.py      # Analytics dashboard
├── utils/
│   ├── __init__.py
│   ├── auth.py           # Authentication manager
│   └── data_manager.py   # Data persistence
├── data/                 # JSON data files (created automatically)
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Usage

1. **Login**: Use existing credentials or register a new account
2. **Admin**: Access system management, user management, and analytics
3. **Customer**: Manage accounts, perform transactions, view history
4. **Analytics**: View detailed transaction patterns and system metrics

## Data Storage

All data is stored in JSON files in the `data/` directory:
- `users.json`: User accounts and authentication
- `accounts.json`: Bank account information
- `transactions.json`: Transaction history

## Security Features

- Password hashing using SHA-256
- Role-based access control
- Session management
- Data validation and error handling

## Future Enhancements

- Database integration (PostgreSQL/MySQL)
- Advanced reporting features
- Mobile responsive design
- API integration
- Email notifications
- Multi-factor authentication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.