from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)

def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS transactions')
        cursor.execute('DROP TABLE IF EXISTS assets')
        cursor.execute('''
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE assets (
                id INTEGER PRIMARY KEY,
                asset_name TEXT NOT NULL,
                asset_value REAL NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT type, category, amount, date FROM transactions ORDER BY date DESC')
        transactions = cursor.fetchall()
    return render_template('index.html', transactions=transactions)

@app.route('/dashboard_data')
def dashboard_data():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT asset_name, asset_value FROM assets')
        assets_data = cursor.fetchall()
        
        cursor.execute('SELECT SUM(amount) FROM transactions')
        total_balance_transactions = cursor.fetchone()[0] or 0
        
        total_balance_assets = sum([x[1] for x in assets_data])
        
        total_balance = total_balance_transactions + total_balance_assets
        
        labels = [x[0] for x in assets_data]
        data = [x[1] for x in assets_data]
        labels.append("Накопления")
        data.append(total_balance_transactions)
    
    return jsonify(labels=labels, data=data, total_balance=total_balance)

@app.route('/current_month_summary')
def current_month_summary():
    now = datetime.now()
    start_of_month = now.replace(day=1)
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(amount) FROM transactions WHERE type="Доход" AND date >= ?', (start_of_month,))
        income = cursor.fetchone()[0] or 0
        cursor.execute('SELECT SUM(amount) FROM transactions WHERE type="Расход" AND date >= ?', (start_of_month,))
        expense = cursor.fetchone()[0] or 0
    return jsonify(income=income, expense=expense)

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        category = request.form['category']
        amount = float(request.form['amount'])
        if amount <= 0:
            return render_template('add_income.html', error="Сумма должна быть больше 0")
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO transactions (type, category, amount) VALUES (?, ?, ?)', ('Доход', category, amount))
            conn.commit()
        return render_template('add_income.html', success=True)
    return render_template('add_income.html')

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        category = request.form['category']
        amount = float(request.form['amount'])
        if amount <= 0:
            return render_template('add_expense.html', error="Сумма должна быть больше 0")
        amount = -amount
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO transactions (type, category, amount) VALUES (?, ?, ?)', ('Расход', category, amount))
            conn.commit()
        return render_template('add_expense.html', success=True)
    return render_template('add_expense.html')

@app.route('/add_asset', methods=['GET', 'POST'])
def add_asset():
    if request.method == 'POST':
        asset_name = request.form['asset_name']
        asset_value = float(request.form['asset_value'])
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO assets (asset_name, asset_value) VALUES (?, ?)', (asset_name, asset_value))
            conn.commit()
        return redirect(url_for('add_asset'))
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, asset_name, asset_value FROM assets')
        assets = cursor.fetchall()
    return render_template('add_asset.html', assets=assets)

@app.route('/delete_asset/<int:asset_id>', methods=['POST'])
def delete_asset(asset_id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM assets WHERE id = ?', (asset_id,))
        conn.commit()
    return redirect(url_for('add_asset'))

@app.route('/get_transactions')
def get_transactions():
    sort_field = request.args.get('sort', 'date')
    filters = {}

    type_filter = request.args.get('type')
    category_filter = request.args.get('category')
    min_amount_filter = request.args.get('min_amount')
    max_amount_filter = request.args.get('max_amount')
    start_date_filter = request.args.get('start_date')
    end_date_filter = request.args.get('end_date')

    sql_query = 'SELECT type, category, amount, date FROM transactions WHERE 1=1'
    params = []

    if type_filter:
        sql_query += ' AND type = ?'
        params.append(type_filter)
    if category_filter:
        sql_query += ' AND category = ?'
        params.append(category_filter)
    if min_amount_filter:
        sql_query += ' AND amount >= ?'
        params.append(float(min_amount_filter))
    if max_amount_filter:
        sql_query += ' AND amount <= ?'
        params.append(float(max_amount_filter))
    if start_date_filter:
        sql_query += ' AND date >= ?'
        params.append(start_date_filter)
    if end_date_filter:
        sql_query += ' AND date <= ?'
        params.append(end_date_filter)

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute(sql_query, params)
        transactions = cursor.fetchall()

    return jsonify(transactions)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
