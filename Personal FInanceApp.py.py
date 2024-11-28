import sqlite3
import getpass
from datetime import datetime

# Database setup
def initialize_db():
    with sqlite3.connect('finance_manager.db') as conn:
        cursor = conn.cursor()
        # Users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')

        # Transactions table
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )''')


        # Budgets table
        # Budgets table
        cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    "limit" REAL NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)''')


# Authentication functions
def register():
    username = input("Enter a username: ")
    password = getpass.getpass("Enter a password: ")

    with sqlite3.connect('finance_manager.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            print("Registration successful.")
        except sqlite3.IntegrityError:
            print("Username already exists.")

def login():
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    with sqlite3.connect('finance_manager.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        if user:
            print("Login successful.")
            return user[0]
        else:
            print("Invalid credentials.")
            return None

# Transaction functions
def add_transaction(user_id):
    transaction_type = input("Enter transaction type (income/expense): ").lower()
    category = input("Enter category: ")
    amount = float(input("Enter amount: "))
    date = input("Enter date (YYYY-MM-DD) or leave blank for today: ") or datetime.today().strftime('%Y-%m-%d')

    with sqlite3.connect('finance_manager.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO transactions (user_id, type, category, amount, date) 
                          VALUES (?, ?, ?, ?, ?)''', (user_id, transaction_type, category, amount, date))
        conn.commit()
        print("Transaction added successfully.")

def update_transaction(user_id):
    transaction_id = int(input("Enter transaction ID to update: "))
    category = input("Enter new category: ")
    amount = float(input("Enter new amount: "))
    date = input("Enter new date (YYYY-MM-DD): ")

    with sqlite3.connect('finance_manager.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''UPDATE transactions SET category = ?, amount = ?, date = ? 
                          WHERE id = ? AND user_id = ?''', (category, amount, date, transaction_id, user_id))
        conn.commit()
        print("Transaction updated successfully.")

def delete_transaction(user_id):
    transaction_id = int(input("Enter transaction ID to delete: "))

    with sqlite3.connect('finance_manager.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?', (transaction_id, user_id))
        conn.commit()
        print("Transaction deleted successfully.")

# Report functions
def generate_report(user_id):
    period = input("Enter report period (monthly/yearly): ").lower()
    year = input("Enter year (YYYY): ")
    month = input("Enter month (MM, optional): ") if period == 'monthly' else None

    with sqlite3.connect('finance_manager.db') as conn:
        cursor = conn.cursor()
        if period == 'monthly':
            cursor.execute('''SELECT type, SUM(amount) FROM transactions 
                              WHERE user_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ? 
                              GROUP BY type''', (user_id, year, month))
        else:
            cursor.execute('''SELECT type, SUM(amount) FROM transactions 
                              WHERE user_id = ? AND strftime('%Y', date) = ? 
                              GROUP BY type''', (user_id, year))

        results = cursor.fetchall()
        income = sum(amount for t_type, amount in results if t_type == 'income')
        expense = sum(amount for t_type, amount in results if t_type == 'expense')
        savings = income - expense

        print(f"Income: {income}, Expense: {expense}, Savings: {savings}")

# Budget functions
def set_budget(user_id):
    category = input("Enter category: ")
    limit = float(input("Enter budget limit: "))

    with sqlite3.connect('finance_manager.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO budgets (user_id, category, limit) VALUES (?, ?, ?)''', (user_id, category, limit))
        conn.commit()
        print("Budget set successfully.")

def check_budget(user_id):
    with sqlite3.connect('finance_manager.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT category, limit FROM budgets WHERE user_id = ?''', (user_id,))
        budgets = cursor.fetchall()

        for category, limit in budgets:
            cursor.execute('''SELECT SUM(amount) FROM transactions 
                              WHERE user_id = ? AND category = ? AND type = 'expense' 
                              AND strftime('%Y-%m', date) = ?''', (user_id, category, datetime.today().strftime('%Y-%m')))
            spent = cursor.fetchone()[0] or 0

            if spent > limit:
                print(f"Warning: You exceeded the budget for {category} (Limit: {limit}, Spent: {spent})")

# Main program
def main():
    initialize_db()
    print("Welcome to the Personal Finance Manager")
    user_id = None

    while not user_id:
        action = input("Choose an action: register, login: ").lower()
        if action == 'register':
            register()
        elif action == 'login':
            user_id = login()

    while True:
        print("\nChoose an option:")
        print("1. Add Transaction")
        print("2. Update Transaction")
        print("3. Delete Transaction")
        print("4. Generate Report")
        print("5. Set Budget")
        print("6. Check Budget")
        print("7. Exit")
        
        choice = input("Enter your choice: ")

        if choice == '1':
            add_transaction(user_id)
        elif choice == '2':
            update_transaction(user_id)
        elif choice == '3':
            delete_transaction(user_id)
        elif choice == '4':
            generate_report(user_id)
        elif choice == '5':
            set_budget(user_id)
        elif choice == '6':
            check_budget(user_id)
        elif choice == '7':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
