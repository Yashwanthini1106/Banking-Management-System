import streamlit as st
import sqlite3 as sq

# Database connection
conn = sq.connect('bank_db.db', check_same_thread=False)
cur = conn.cursor()

# Create table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS bank_db(
    Name TEXT PRIMARY KEY,
    password TEXT,
    pin INTEGER,
    acc_balance INTEGER
)
""")
conn.commit()


class Bank:

    def __init__(self):
        st.title("🏦 Welcome to AKD Bank")

        if 'logged' not in st.session_state:
            st.session_state.logged = False
            st.session_state.user = ""
            st.session_state.pin = ""
            st.session_state.balance = 0

    # ---------------- LOGIN ----------------

    def login(self):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            query = "SELECT * FROM bank_db WHERE Name=?"
            cur.execute(query, (username,))
            row = cur.fetchone()

            if row is None:
                st.warning("Invalid Username")
                return

            db_name, db_password, db_pin, db_balance = row

            if password != db_password:
                st.error("Incorrect Password")
                return

            st.session_state.logged = True
            st.session_state.user = db_name
            st.session_state.pin = db_pin
            st.session_state.balance = db_balance

        if st.session_state.logged:

            st.success(f"Welcome {st.session_state.user}")

            service = st.selectbox(
                "Select Service",
                ["Deposit", "Withdraw", "Check Balance", "Mini Statement"]
            )

            if service == "Deposit":
                self.deposit()

            elif service == "Withdraw":
                self.withdraw()

            elif service == "Check Balance":
                self.check_balance()

            elif service == "Mini Statement":
                self.mini_statement()

    # ---------------- SIGNUP ----------------

    def signup(self):

        username = st.text_input("Create Username")
        password = st.text_input("Create Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        pin = st.number_input("Set 4 Digit PIN", min_value=1000, max_value=9999)
        confirm_pin = st.number_input("Confirm PIN", min_value=1000, max_value=9999)

        if st.button("Create Account"):

            if password != confirm_password:
                st.error("Passwords do not match")
                return

            if pin != confirm_pin:
                st.error("PIN does not match")
                return

            try:
                cur.execute(
                    "INSERT INTO bank_db VALUES (?,?,?,?)",
                    (username, password, pin, 0)
                )
                conn.commit()

                st.success("Account created successfully!")

            except:
                st.warning("Username already exists")

    # ---------------- DEPOSIT ----------------

    def deposit(self):

        pin = st.text_input("Enter PIN", type="password")

        if pin == str(st.session_state.pin):

            amount = st.number_input("Enter Deposit Amount", min_value=0)

            if st.button("Deposit"):

                if amount < 100:
                    st.warning("Minimum deposit is ₹100")
                    return

                new_balance = st.session_state.balance + amount

                cur.execute(
                    "UPDATE bank_db SET acc_balance=? WHERE Name=?",
                    (new_balance, st.session_state.user)
                )

                conn.commit()

                st.session_state.balance = new_balance

                st.success("Amount deposited successfully")

        elif pin != "":
            st.error("Invalid PIN")

    # ---------------- WITHDRAW ----------------

    def withdraw(self):

        pin = st.text_input("Enter PIN", type="password")

        if pin == str(st.session_state.pin):

            amount = st.number_input("Enter Withdrawal Amount", min_value=0)

            if st.button("Withdraw"):

                if amount < 100:
                    st.warning("Minimum withdrawal ₹100")
                    return

                if amount > st.session_state.balance:
                    st.error("Insufficient Balance")
                    return

                new_balance = st.session_state.balance - amount

                cur.execute(
                    "UPDATE bank_db SET acc_balance=? WHERE Name=?",
                    (new_balance, st.session_state.user)
                )

                conn.commit()

                st.session_state.balance = new_balance

                st.success("Amount withdrawn successfully")

        elif pin != "":
            st.error("Invalid PIN")

    # ---------------- CHECK BALANCE ----------------

    def check_balance(self):

        pin = st.text_input("Enter PIN", type="password")

        if pin == str(st.session_state.pin):
            st.success(f"Current Balance: ₹{st.session_state.balance}")

        elif pin != "":
            st.error("Invalid PIN")

    # ---------------- MINI STATEMENT ----------------

    def mini_statement(self):

        pin = st.text_input("Enter PIN", type="password")

        if pin == str(st.session_state.pin):

            st.subheader("Mini Statement")

            st.write("Account Holder:", st.session_state.user)
            st.write("Available Balance:", st.session_state.balance)

        elif pin != "":
            st.error("Invalid PIN")


# ---------------- MAIN PROGRAM ----------------

bank = Bank()

menu = st.sidebar.selectbox("Menu", ["Signup", "Login"])

if menu == "Signup":
    bank.signup()

elif menu == "Login":
    bank.login()
