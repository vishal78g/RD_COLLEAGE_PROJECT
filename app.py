from flask import Flask, render_template, request, jsonify, url_for
import os
import json
import sqlite3


app = Flask(__name__)


#Data base connection
DB_PATH = os.path.join(app.root_path, 'rd_accounts.db')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS accounts (
                account_no TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                name TEXT NOT NULL,
                address TEXT,
                mobile TEXT,
                aadhar TEXT,
                agent_id TEXT,
                monthly_amount REAL,
                duration INTEGER,
                start_date TEXT,
                maturity_date TEXT,
                maturity_amount REAL,
                installments TEXT NOT NULL DEFAULT '[]'
            )
            '''
        )


def seed_sample_data():
    sample_accounts = [
        {
            'customerId': 'C1001',
            'name': 'Rahul Sharma',
            'address': 'Mumbai, Maharashtra',
            'mobile': '9876543210',
            'aadhar': '123456789012',
            'accountNo': 'RD1001',
            'agentId': 'AG102',
            'monthlyAmount': 1000,
            'duration': 60,
            'startDate': '2026-01-01',
            'maturityDate': '2031-01-01',
            'maturityAmount': 72000,
            'installments': [
                {'month': '2026-01', 'depositDate': '2026-01-05', 'amount': 1000, 'status': 'Paid'},
                {'month': '2026-02', 'depositDate': '2026-02-05', 'amount': 1000, 'status': 'Paid'}
            ]
        },
        {
            'customerId': 'C1002',
            'name': 'Priya Patel',
            'address': 'Surat, Gujarat',
            'mobile': '9988776655',
            'aadhar': '234567890123',
            'accountNo': 'RD1002',
            'agentId': 'AG102',
            'monthlyAmount': 1500,
            'duration': 48,
            'startDate': '2026-01-10',
            'maturityDate': '2030-01-10',
            'maturityAmount': 86400,
            'installments': [
                {'month': '2026-01', 'depositDate': '2026-01-12', 'amount': 1500, 'status': 'Paid'}
            ]
        },
        {
            'customerId': 'C1003',
            'name': 'Amit Kumar',
            'address': 'Pune, Maharashtra',
            'mobile': '9123456780',
            'aadhar': '345678901234',
            'accountNo': 'RD1003',
            'agentId': 'AG103',
            'monthlyAmount': 2000,
            'duration': 36,
            'startDate': '2026-02-01',
            'maturityDate': '2029-02-01',
            'maturityAmount': 86400,
            'installments': []
        }
    ]

    with get_db_connection() as conn:
        count_row = conn.execute('SELECT COUNT(*) AS total FROM accounts').fetchone()
        if count_row['total'] > 0:
            return

        conn.executemany(
            '''
            INSERT INTO accounts (
                account_no, customer_id, name, address, mobile, aadhar, agent_id,
                monthly_amount, duration, start_date, maturity_date, maturity_amount, installments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            [
                (
                    account['accountNo'],
                    account['customerId'],
                    account['name'],
                    account['address'],
                    account['mobile'],
                    account['aadhar'],
                    account['agentId'],
                    account['monthlyAmount'],
                    account['duration'],
                    account['startDate'],
                    account['maturityDate'],
                    account['maturityAmount'],
                    json.dumps(account['installments'])
                )
                for account in sample_accounts
            ]
        )


def row_to_account(row):
    try:
        installments = json.loads(row['installments'] or '[]')
    except json.JSONDecodeError:
        installments = []

    return {
        'customerId': row['customer_id'],
        'name': row['name'],
        'address': row['address'] or '',
        'mobile': row['mobile'] or '',
        'aadhar': row['aadhar'] or '',
        'accountNo': row['account_no'],
        'agentId': row['agent_id'] or '',
        'monthlyAmount': row['monthly_amount'] or 0,
        'duration': row['duration'] or 0,
        'startDate': row['start_date'] or '',
        'maturityDate': row['maturity_date'] or '',
        'maturityAmount': row['maturity_amount'] or 0,
        'installments': installments
    }


def get_account_from_db(account_no):
    with get_db_connection() as conn:
        row = conn.execute(
            'SELECT * FROM accounts WHERE account_no = ?',
            (account_no,)
        ).fetchone()

    return row_to_account(row) if row else None


def normalize_account_payload(payload):
    monthly_amount = float(payload.get('monthlyAmount') or 0)
    duration = int(payload.get('duration') or 0)
    maturity_amount = payload.get('maturityAmount')

    if maturity_amount in (None, ''):
        maturity_amount = round(monthly_amount * duration * 1.2, 2)
    else:
        maturity_amount = float(maturity_amount)

    return {
        'customerId': (payload.get('customerId') or '').strip(),
        'name': (payload.get('name') or '').strip(),
        'address': (payload.get('address') or '').strip(),
        'mobile': (payload.get('mobile') or '').strip(),
        'aadhar': (payload.get('aadhar') or '').strip(),
        'accountNo': (payload.get('accountNo') or '').strip(),
        'agentId': (payload.get('agentId') or '').strip(),
        'monthlyAmount': monthly_amount,
        'duration': duration,
        'startDate': payload.get('startDate') or '',
        'maturityDate': payload.get('maturityDate') or '',
        'maturityAmount': maturity_amount,
        'installments': payload.get('installments') or []
    }


def validate_account_payload(account):
    if not account['accountNo']:
        return 'Account No is required.'
    if not account['customerId']:
        return 'Customer ID is required.'
    if not account['name']:
        return 'Customer name is required.'
    return None


init_db()
seed_sample_data()


#Login page 
@app.route("/")
def home():
    return render_template("login.html")
    
 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        agent_id = request.form.get('agentId')
        password = request.form.get('password')

        # Replace with your actual validation
        if agent_id == "admin" and password == "admin":
            return jsonify({"status": "success", "redirect": url_for('dashboard')})
        else:
            return jsonify({"status": "error", "message": "Invalid Credentials"}), 401

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
    
@app.route('/new-account')
@app.route('/NewAccount')
def new_account():
    return render_template('NewAccount.html')
    
@app.route('/deposit')
@app.route('/Deposit')
def deposit():
    return render_template('Deposit.html')
    
@app.route('/account-details')
@app.route('/accountDetails')
def account_details():
    return render_template('account details.html')


@app.route('/accounts-list')
@app.route('/accountsList')
def accounts_list():
    return render_template('AccountsList.html')
    
@app.route('/monthly-report')
@app.route('/MonthlyReport')
def monthly_report():
    return render_template('MonthlyReport.html')

@app.route('/agent-profile')
@app.route('/agentProfile')
def agent_profile():
    return render_template('agent_profile.html')


@app.route('/api/accounts', methods=['GET'])
def list_accounts():
    query = (request.args.get('query') or '').strip().lower()
    with get_db_connection() as conn:
        if query:
            like_query = f'%{query}%'
            rows = conn.execute(
                '''
                SELECT * FROM accounts
                WHERE LOWER(account_no) LIKE ?
                   OR LOWER(customer_id) LIKE ?
                   OR LOWER(name) LIKE ?
                ORDER BY account_no ASC
                ''',
                (like_query, like_query, like_query)
            ).fetchall()
        else:
            rows = conn.execute(
                'SELECT * FROM accounts ORDER BY account_no ASC'
            ).fetchall()

    data = [row_to_account(row) for row in rows]

    return jsonify({'status': 'success', 'data': data})


@app.route('/api/accounts', methods=['POST'])
def create_account():
    payload = request.get_json(silent=True) or {}
    account = normalize_account_payload(payload)

    error = validate_account_payload(account)
    if error:
        return jsonify({'status': 'error', 'message': error}), 400

    account_no = account['accountNo']
    if get_account_from_db(account_no):
        return jsonify({'status': 'error', 'message': 'Account already exists.'}), 409

    with get_db_connection() as conn:
        conn.execute(
            '''
            INSERT INTO accounts (
                account_no, customer_id, name, address, mobile, aadhar, agent_id,
                monthly_amount, duration, start_date, maturity_date, maturity_amount, installments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                account['accountNo'],
                account['customerId'],
                account['name'],
                account['address'],
                account['mobile'],
                account['aadhar'],
                account['agentId'],
                account['monthlyAmount'],
                account['duration'],
                account['startDate'],
                account['maturityDate'],
                account['maturityAmount'],
                json.dumps(account['installments'])
            )
        )

    return jsonify({'status': 'success', 'message': 'Account created successfully.', 'data': account}), 201


@app.route('/api/accounts/<account_no>', methods=['GET'])
def get_account(account_no):
    account = get_account_from_db(account_no)
    if not account:
        return jsonify({'status': 'error', 'message': 'Account not found.'}), 404

    return jsonify({'status': 'success', 'data': account})


@app.route('/api/accounts/<account_no>', methods=['PUT'])
def update_account(account_no):
    existing = get_account_from_db(account_no)
    if not existing:
        return jsonify({'status': 'error', 'message': 'Account not found.'}), 404

    payload = request.get_json(silent=True) or {}
    incoming = normalize_account_payload(payload)

    error = validate_account_payload(incoming)
    if error:
        return jsonify({'status': 'error', 'message': error}), 400

    new_account_no = incoming['accountNo']
    if new_account_no != account_no and get_account_from_db(new_account_no):
        return jsonify({'status': 'error', 'message': 'New account number already exists.'}), 409

    with get_db_connection() as conn:
        if new_account_no != account_no:
            conn.execute('DELETE FROM accounts WHERE account_no = ?', (account_no,))

        conn.execute(
            '''
            INSERT OR REPLACE INTO accounts (
                account_no, customer_id, name, address, mobile, aadhar, agent_id,
                monthly_amount, duration, start_date, maturity_date, maturity_amount, installments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                incoming['accountNo'],
                incoming['customerId'],
                incoming['name'],
                incoming['address'],
                incoming['mobile'],
                incoming['aadhar'],
                incoming['agentId'],
                incoming['monthlyAmount'],
                incoming['duration'],
                incoming['startDate'],
                incoming['maturityDate'],
                incoming['maturityAmount'],
                json.dumps(incoming['installments'])
            )
        )

    return jsonify({'status': 'success', 'message': 'Account updated successfully.', 'data': incoming})


@app.route('/api/accounts/<account_no>', methods=['DELETE'])
def delete_account(account_no):
    existing = get_account_from_db(account_no)
    if not existing:
        return jsonify({'status': 'error', 'message': 'Account not found.'}), 404

    with get_db_connection() as conn:
        conn.execute('DELETE FROM accounts WHERE account_no = ?', (account_no,))

    return jsonify({'status': 'success', 'message': 'Account deleted successfully.', 'data': existing})

    
if __name__ == "__main__":
    app.run(debug = True)