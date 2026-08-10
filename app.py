from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


# Create database and table
def init_db():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL
        )
    """)

    # Add category column if it doesn't already exist
    cursor.execute("PRAGMA table_info(expenses)")
    columns = [column[1] for column in cursor.fetchall()]

    if "category" not in columns:
        cursor.execute(
            "ALTER TABLE expenses ADD COLUMN category TEXT DEFAULT 'Other'"
        )


    conn.commit()
    conn.close()



@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        expense_name = request.form["expense_name"]
        amount = request.form["amount"]

        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO expenses (name, amount) VALUES (?, ?)",
            (expense_name, amount)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    conn = sqlite3.connect("expenses.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()

    conn.close()

    total = sum(float(expense["amount"]) for expense in expenses)

    return render_template(
        "index.html",
        expenses=expenses,
        total=total
    )


@app.route("/delete/<int:index>")
def delete_expense(index):

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (index,)
    )

    conn.commit()
    conn.close()

    return redirect("/") 
@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit_expense(index):

    conn = sqlite3.connect("expenses.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":
        expense_name = request.form["expense_name"]
        amount = request.form["amount"]

        cursor.execute(
            "UPDATE expenses SET name = ?, amount = ? WHERE id = ?",
            (expense_name, amount, index)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    cursor.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (index,)
    )

    expense = cursor.fetchone()

    conn.close()

    return render_template(
        "edit.html",
        expense=expense
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)