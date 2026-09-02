import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    raise_on_warnings=True
)

cursor = conn.cursor()

print("Connected Successfully")

while True:
    print("\n===== BANK MENU =====")
    print("1. Create Account")
    print("2. View Accounts")
    print("3. Deposit Money")
    print("4. Withdraw Money")
    print("5. Delete Account")
    print("6. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        name = input("Enter name: ")
        balance = float(input("Enter opening balance: "))

        sql = "INSERT INTO bank (name, balance) VALUES (%s, %s)"
        values = (name, balance)

        cursor.execute(sql, values)
        conn.commit()

        print("Account Created Successfully")

    elif choice == "2":
        cursor.execute("SELECT * FROM bank")
        rows = cursor.fetchall()

        print("\nID\tNAME\tBALANCE")

        for row in rows:
            print(row[0], "\t", row[1], "\t", row[2])

    elif choice == "3":
        id = int(input("Enter Account ID: "))
        amount = float(input("Enter Deposit Amount: "))

        sql = "UPDATE bank SET balance = balance + %s WHERE id = %s"
        values = (amount, id)

        cursor.execute(sql, values)
        conn.commit()

        print("Amount Deposited Successfully")

    elif choice == "4":
        id = int(input("Enter Account ID: "))
        amount = float(input("Enter Withdrawal Amount: "))

        sql = "UPDATE bank SET balance = balance - %s WHERE id = %s"
        values = (amount, id)

        cursor.execute(sql, values)
        conn.commit()

        print("Amount Withdrawn Successfully")

    elif choice == "5":
        id = int(input("Enter Account ID to Delete: "))

        sql = "DELETE FROM bank WHERE id = %s"
        values = (id,)

        cursor.execute(sql, values)
        conn.commit()

        print("Account Deleted Successfully")

    elif choice == "6":
        print("Exiting...")
        break

    else:
        print("Invalid Choice. Please try again.")

cursor.close()
conn.close()

