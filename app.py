from flask import Flask, render_template,request,jsonify
import os


app = Flask(__name__)


#Data base connection



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
            return jsonify({"status": "success", "redirect": "/dashboard"})
        else:
            return jsonify({"status": "error", "message": "Invalid Credentials"}), 401

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # This serves your dashboard.html file
    return render_template('dashboard.html')
    
@app.route('/NewAccount')
def newAccount():
    # This serves your NewAccount.html file
    return render_template('NewAccount.html')
    
    
@app.route('/Deposit')
def Deposit():
    # This serves your Deposit.html file
    return render_template(Deposit)
    
@app.route('/accountDetails')
def accountDetails():
    # This serves your accountDetails.html file
    return render_template(accountDetails)
    
@app.route('/MonthlyReport')
def MonthlyReport():
    # This serves your MonthlyReport.html file
    return render_template(MonthlyReport)

@app.route('/agentProfile')
def agentProfile():
    # This serves your agentProfile.html file
    return render_template(agentProfile)

    
if __name__ == "__main__":
    app.run(debug = True)