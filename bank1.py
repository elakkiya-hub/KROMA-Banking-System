import streamlit as st
import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


# ================= DATABASE =================

def db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


# ================= PAGE =================

st.set_page_config(
    page_title="KROMA Banking",
    page_icon="🏦",
    layout="wide"
)


# ================= STYLE =================

st.markdown("""
<style>

.stApp {
    background-color: #f4f7fb;
}

section[data-testid="stSidebar"] {
    background-color: #0b2d5c;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

h1, h2, h3 {
    color: #0b2d5c !important;
}

.stButton > button {
    background-color: #0b2d5c;
    color: white;
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)


# ================= SESSION =================

if "login" not in st.session_state:
    st.session_state.login = False

if "role" not in st.session_state:
    st.session_state.role = ""

if "user_id" not in st.session_state:
    st.session_state.user_id = None


# =========================================================
# LOGIN PAGE
# =========================================================

if not st.session_state.login:

    st.markdown(
        "<h1 style='text-align:center;'>🏦 KROMA</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center;color:gray;'>"
        "BANKING MANAGEMENT SYSTEM"
        "</p>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.subheader("🔐 Login")

        login_type = st.radio(
            "Login As",
            ["👨‍💼 Admin", "👤 User"],
            horizontal=True
        )


        # =================================================
        # ADMIN LOGIN
        # =================================================

        if login_type == "👨‍💼 Admin":

            admin_id = st.number_input(
                "Admin ID",
                min_value=1,
                step=1
            )

            admin_password = st.text_input(
                "Admin Password",
                type="password"
            )

            if st.button(
                "🔐 Admin Login",
                use_container_width=True
            ):

                if admin_id == 1 and admin_password == "admin123":

                    st.session_state.login = True
                    st.session_state.role = "admin"
                    st.session_state.user_id = 1

                    st.rerun()

                else:

                    st.error(
                        "Invalid Admin ID or Password!"
                    )


        # =================================================
        # USER LOGIN
        # =================================================

        else:

            user_id = st.number_input(
                "User ID",
                min_value=1,
                step=1
            )

            user_pin = st.text_input(
                "4-Digit PIN",
                type="password",
                max_chars=4
            )

            if st.button(
                "🔐 User Login",
                use_container_width=True
            ):

                try:

                    conn = db()
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        SELECT id
                        FROM bank
                        WHERE id=%s
                        AND pin=%s
                        AND role='user'
                        """,
                        (user_id, user_pin)
                    )

                    result = cursor.fetchone()

                    conn.close()

                    if result:

                        st.session_state.login = True
                        st.session_state.role = "user"
                        st.session_state.user_id = result[0]

                        st.rerun()

                    else:

                        st.error(
                            "Invalid User ID or PIN!"
                        )

                except Exception as e:

                    st.error(
                        f"Database Error: {e}"
                    )


# =========================================================
# ADMIN
# =========================================================

elif st.session_state.role == "admin":

    st.sidebar.title("🏦 KROMA")
    st.sidebar.write("👨‍💼 Admin")
    st.sidebar.markdown("---")

    menu = st.sidebar.radio(
        "ADMIN MENU",
        [
            "👥 Account View",
            "➕ Create Account",
            "🔑 Password",
            "🗑️ Delete Account",
            "💰 Check Balance",
            "📊 Transaction History",
            "🚪 Exit"
        ]
    )


    # =====================================================
    # ADMIN - ACCOUNT VIEW
    # =====================================================

    if menu == "👥 Account View":

        st.title("👥 Customer Accounts")

        try:

            conn = db()

            # SEARCH
            search = st.text_input(
                "🔍 Search by User ID or Name",
                placeholder="Enter ID or customer name"
            )

            if search.strip():

                if search.isdigit():

                    df = pd.read_sql(
                        """
                        SELECT
                            id,
                            name,
                            pin,
                            balance,
                            created_at
                        FROM bank
                        WHERE role='user'
                        AND id=%s
                        """,
                        conn,
                        params=(int(search),)
                    )

                else:

                    df = pd.read_sql(
                        """
                        SELECT
                            id,
                            name,
                            pin,
                            balance,
                            created_at
                        FROM bank
                        WHERE role='user'
                        AND name LIKE %s
                        """,
                        conn,
                        params=(f"%{search}%",)
                    )

            else:

                df = pd.read_sql(
                    """
                    SELECT
                        id,
                        name,
                        pin,
                        balance,
                        created_at
                    FROM bank
                    WHERE role='user'
                    """,
                    conn
                )

            conn.close()

            if not df.empty:

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                st.success(
                    f"Total Accounts Found: {len(df)}"
                )

            else:

                st.info(
                    "No customer accounts found."
                )

        except Exception as e:

            st.error(
                f"Error: {e}"
            )


    # =====================================================
    # ADMIN - CREATE ACCOUNT
    # =====================================================

    elif menu == "➕ Create Account":

        st.title("➕ Create New Account")

        name = st.text_input(
            "Customer Name"
        )

        amount = st.number_input(
            "Initial Deposit",
            min_value=1000.0,
            value=1000.0,
            step=100.0
        )

        display_name = name if name else "Customer"

        st.info(
            f"👤 Name: {display_name} | "
            f"💰 Available Balance: ₹{amount:,.2f}"
        )

        pin = st.text_input(
            "Create 4-Digit PIN",
            type="password",
            max_chars=4
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if name.strip() == "" or pin == "":

                st.warning(
                    "Please enter all details."
                )

            elif len(pin) != 4 or not pin.isdigit():

                st.warning(
                    "PIN must contain exactly 4 digits."
                )

            else:

                try:

                    conn = db()
                    cursor = conn.cursor()

                    # CREATE ACCOUNT
                    cursor.execute(
                        """
                        INSERT INTO bank
                        (name, balance, pin, role)
                        VALUES (%s, %s, %s, 'user')
                        """,
                        (name.strip(), amount, pin)
                    )

                    new_id = cursor.lastrowid

                    # INITIAL DEPOSIT TRANSACTION
                    cursor.execute(
                        """
                        INSERT INTO transactions
                        (user_id, type, amount, balance_after)
                        VALUES (%s, 'Deposit', %s, %s)
                        """,
                        (new_id, amount, amount)
                    )

                    conn.commit()
                    conn.close()

                    st.success(
                        "✅ Account Created Successfully!"
                    )

                    st.info(
                        f"👤 Name: {name.strip()} | "
                        f"💰 Available Balance: ₹{amount:,.2f}"
                    )

                    st.success(
                        f"🆔 User ID: {new_id}"
                    )

                except Exception as e:

                    st.error(
                        f"Error: {e}"
                    )


    # =====================================================
    # ADMIN - PASSWORD
    # =====================================================

    elif menu == "🔑 Password":

        st.title("🔑 Admin Password")

        st.info("Admin ID: 1")
        st.info("Admin Password: admin123")


    # =====================================================
    # ADMIN - DELETE ACCOUNT
    # =====================================================

    elif menu == "🗑️ Delete Account":

        st.title("🗑️ Delete Customer Account")

        try:

            conn = db()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, name, balance
                FROM bank
                WHERE role='user'
                """
            )

            users = cursor.fetchall()

            if users:

                selected = st.selectbox(
                    "Select Customer",
                    users,
                    format_func=lambda x:
                    f"ID: {x[0]} - {x[1]} - ₹{float(x[2]):,.2f}"
                )

                st.warning(
                    "⚠️ This account will be permanently deleted."
                )

                if st.button(
                    "🗑️ Delete Account",
                    use_container_width=True
                ):

                    # DELETE TRANSACTIONS
                    cursor.execute(
                        """
                        DELETE FROM transactions
                        WHERE user_id=%s
                        """,
                        (selected[0],)
                    )

                    # DELETE ACCOUNT
                    cursor.execute(
                        """
                        DELETE FROM bank
                        WHERE id=%s
                        AND role='user'
                        """,
                        (selected[0],)
                    )

                    conn.commit()
                    conn.close()

                    st.success(
                        "Account Deleted Successfully!"
                    )

                    st.rerun()

            else:

                st.info(
                    "No customer accounts found."
                )

                conn.close()

        except Exception as e:

            st.error(
                f"Error: {e}"
            )


    # =====================================================
    # ADMIN - CHECK BALANCE
    # =====================================================

    elif menu == "💰 Check Balance":

        st.title("💰 All Customer Balances")

        try:

            conn = db()

            df = pd.read_sql(
                """
                SELECT
                    id,
                    name,
                    balance
                FROM bank
                WHERE role='user'
                ORDER BY id
                """,
                conn
            )

            conn.close()

            if not df.empty:

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No customer accounts found."
                )

        except Exception as e:

            st.error(
                f"Error: {e}"
            )


    # =====================================================
    # ADMIN - TRANSACTION HISTORY
    # =====================================================

    elif menu == "📊 Transaction History":

        st.title("📊 All Transaction History")

        try:

            conn = db()

            # TRANSACTION TYPE FILTER
            transaction_filter = st.selectbox(
                "🔽 Filter Transaction",
                [
                    "All",
                    "Deposit",
                    "Withdraw"
                ]
            )

            # SEARCH
            search = st.text_input(
                "🔍 Search by User ID or Name"
            )

            query = """
                SELECT
                    t.trans_id AS Transaction_ID,
                    t.user_id AS User_ID,
                    b.name AS Name,
                    t.type AS Type,
                    t.amount AS Amount,
                    t.balance_after AS Balance,
                    t.created_at AS Date
                FROM transactions t
                JOIN bank b
                ON t.user_id = b.id
                WHERE 1=1
            """

            params = []

            # TYPE FILTER
            if transaction_filter != "All":

                query += " AND t.type=%s"
                params.append(transaction_filter)

            # SEARCH FILTER
            if search.strip():

                if search.isdigit():

                    query += " AND t.user_id=%s"
                    params.append(int(search))

                else:

                    query += " AND b.name LIKE %s"
                    params.append(f"%{search}%")

            query += " ORDER BY t.created_at DESC"

            df = pd.read_sql(
                query,
                conn,
                params=params
            )

            conn.close()

            if not df.empty:

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                st.success(
                    f"Transactions Found: {len(df)}"
                )

            else:

                st.info(
                    "No transactions found."
                )

        except Exception as e:

            st.error(
                f"Error: {e}"
            )


    # =====================================================
    # ADMIN - EXIT
    # =====================================================

    elif menu == "🚪 Exit":

        st.session_state.login = False
        st.session_state.role = ""
        st.session_state.user_id = None

        st.rerun()


# =========================================================
# USER
# =========================================================

else:

    st.sidebar.title("🏦 KROMA")
    st.sidebar.write("👤 User")
    st.sidebar.markdown("---")

    menu = st.sidebar.radio(
        "USER MENU",
        [
            "👤 My Account",
            "💰 Deposit",
            "💸 Withdraw",
            "💳 Check Balance",
            "📊 My Transactions",
            "🚪 Logout",
            "🚪 Exit"
        ]
    )

    uid = st.session_state.user_id


    # =====================================================
    # USER - MY ACCOUNT
    # =====================================================

    if menu == "👤 My Account":

        st.title("👤 My Account")

        try:

            conn = db()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    pin,
                    balance,
                    created_at
                FROM bank
                WHERE id=%s
                AND role='user'
                """,
                (uid,)
            )

            user = cursor.fetchone()

            conn.close()

            if user:

                st.write(f"**🆔 User ID:** {user[0]}")
                st.write(f"**👤 Name:** {user[1]}")
                st.write(f"**🔑 PIN:** {user[2]}")

                st.write(
                    f"**💰 Available Balance:** "
                    f"₹{float(user[3]):,.2f}"
                )

                st.write(
                    f"**📅 Created:** {user[4]}"
                )

        except Exception as e:

            st.error(
                f"Error: {e}"
            )


    # =====================================================
    # USER - DEPOSIT
    # =====================================================

    elif menu == "💰 Deposit":

        st.title("💰 Deposit Money")

        try:

            conn = db()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT name, balance
                FROM bank
                WHERE id=%s
                AND role='user'
                """,
                (uid,)
            )

            user = cursor.fetchone()

            if user:

                name = user[0]
                balance = float(user[1])

                st.info(
                    f"👤 Name: {name} | "
                    f"💰 Available Balance: ₹{balance:,.2f}"
                )

                amount = st.number_input(
                    "Deposit Amount",
                    min_value=1.0,
                    step=100.0
                )

                new_balance = balance + amount

                st.success(
                    f"After Deposit → "
                    f"₹{new_balance:,.2f}"
                )

                if st.button(
                    "💰 Deposit",
                    use_container_width=True
                ):

                    # UPDATE BALANCE
                    cursor.execute(
                        """
                        UPDATE bank
                        SET balance=%s
                        WHERE id=%s
                        AND role='user'
                        """,
                        (new_balance, uid)
                    )

                    # SAVE TRANSACTION
                    cursor.execute(
                        """
                        INSERT INTO transactions
                        (user_id, type, amount, balance_after)
                        VALUES (%s, 'Deposit', %s, %s)
                        """,
                        (uid, amount, new_balance)
                    )

                    conn.commit()
                    conn.close()

                    st.success(
                        f"₹{amount:,.2f} Deposited Successfully!"
                    )

                    st.info(
                        f"👤 {name} | "
                        f"💰 Available Balance: "
                        f"₹{new_balance:,.2f}"
                    )

            else:

                conn.close()

        except Exception as e:

            st.error(
                f"Error: {e}"
            )


    # =====================================================
    # USER - WITHDRAW
    # =====================================================

    elif menu == "💸 Withdraw":

        st.title("💸 Withdraw Money")

        try:

            conn = db()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT name, balance
                FROM bank
                WHERE id=%s
                AND role='user'
                """,
                (uid,)
            )

            user = cursor.fetchone()

            if user:

                name = user[0]
                balance = float(user[1])

                st.info(
                    f"👤 Name: {name} | "
                    f"💰 Available Balance: ₹{balance:,.2f}"
                )

                amount = st.number_input(
                    "Withdraw Amount",
                    min_value=1.0,
                    step=100.0
                )

                if amount <= balance:

                    new_balance = balance - amount

                    st.warning(
                        f"After Withdrawal → "
                        f"₹{new_balance:,.2f}"
                    )

                else:

                    new_balance = balance

                    st.error(
                        "Insufficient Balance!"
                    )

                if st.button(
                    "💸 Withdraw",
                    use_container_width=True
                ):

                    if amount <= balance:

                        # UPDATE BALANCE
                        cursor.execute(
                            """
                            UPDATE bank
                            SET balance=%s
                            WHERE id=%s
                            AND role='user'
                            """,
                            (new_balance, uid)
                        )

                        # SAVE TRANSACTION
                        cursor.execute(
                            """
                            INSERT INTO transactions
                            (user_id, type, amount, balance_after)
                            VALUES (%s, 'Withdraw', %s, %s)
                            """,
                            (uid, amount, new_balance)
                        )

                        conn.commit()
                        conn.close()

                        st.success(
                            f"₹{amount:,.2f} Withdrawn Successfully!"
                        )

                        st.info(
                            f"👤 {name} | "
                            f"💰 Available Balance: "
                            f"₹{new_balance:,.2f}"
                        )

                    else:

                        st.error(
                            "Insufficient Balance!"
                        )

            else:

                conn.close()

        except Exception as e:

            st.error(
                f"Error: {e}"
            )


    # =====================================================
    # USER - CHECK BALANCE
    # =====================================================

    elif menu == "💳 Check Balance":

        st.title("💳 My Balance")

        try:

            conn = db()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT name, balance
                FROM bank
                WHERE id=%s
                AND role='user'
                """,
                (uid,)
            )

            result = cursor.fetchone()

            conn.close()

            if result:

                st.metric(
                    f"👤 {result[0]}",
                    f"₹{float(result[1]):,.2f}"
                )

        except Exception as e:

            st.error(
                f"Error: {e}"
            )


    # =====================================================
    # USER - MY TRANSACTIONS
    # =====================================================

    elif menu == "📊 My Transactions":

        st.title("📊 My Transaction History")

        try:

            conn = db()

            transaction_filter = st.selectbox(
                "🔽 Filter Transaction",
                [
                    "All",
                    "Deposit",
                    "Withdraw"
                ]
            )

            if transaction_filter == "All":

                df = pd.read_sql(
                    """
                    SELECT
                        trans_id AS Transaction_ID,
                        type AS Type,
                        amount AS Amount,
                        balance_after AS Balance,
                        created_at AS Date
                    FROM transactions
                    WHERE user_id=%s
                    ORDER BY created_at DESC
                    """,
                    conn,
                    params=(uid,)
                )

            else:

                df = pd.read_sql(
                    """
                    SELECT
                        trans_id AS Transaction_ID,
                        type AS Type,
                        amount AS Amount,
                        balance_after AS Balance,
                        created_at AS Date
                    FROM transactions
                    WHERE user_id=%s
                    AND type=%s
                    ORDER BY created_at DESC
                    """,
                    conn,
                    params=(uid, transaction_filter)
                )

            conn.close()

            if not df.empty:

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                st.success(
                    f"Transactions Found: {len(df)}"
                )

            else:

                st.info(
                    "No transactions found."
                )

        except Exception as e:

            st.error(
                f"Error: {e}"
            )


    # =====================================================
    # USER - LOGOUT
    # =====================================================

    elif menu == "🚪 Logout":

        st.session_state.login = False
        st.session_state.role = ""
        st.session_state.user_id = None

        st.rerun()


    # =====================================================
    # USER - EXIT
    # =====================================================

    elif menu == "🚪 Exit":

        st.session_state.login = False
        st.session_state.role = ""
        st.session_state.user_id = None

        st.rerun()