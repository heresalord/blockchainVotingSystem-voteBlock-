from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import datetime
import time

from blockchain import Blockchain
from auth import authenticate_user
from vote_timer import start_vote_timer
from utils import time_remaining, filter_data_based_on_time

app = Flask(__name__)
app.secret_key = b"your_persistent_secret_key_here"  # Replace with a constant key for session persistence

blockchain = Blockchain()

vote_duration = 300
start_time = time.time()
start_vote_timer(blockchain, vote_duration)

@app.route("/vote", methods=["GET", "POST"])
def vote():
    if not session.get('authenticated', False):
        return redirect(url_for('login'))

    if session.get('authenticated_role', '').lower() == 'admin':
        return redirect(url_for('display_results'))

    if request.method == "POST":
        full_name = session.get('authenticated_full_name', None)
        npi = session.get('authenticated_npi', None)
        choice = request.form["choice"]
        if blockchain.vote_closed:
            return render_template("Vote/vote.html", message="The vote is closed!")
        hash_value = blockchain.record_vote(full_name, npi, choice)
        if hash_value == "Your vote has already been recorded!":
            return render_template("Vote/vote.html", message=hash_value)
        else:
            return render_template("vote_success/vote_success.html", hash_value=hash_value, end_time=(datetime.datetime.now() + datetime.timedelta(seconds=180)))
    return render_template("Vote/vote.html", active_page="vote")

@app.route("/", methods=["GET"])
def home():
    return render_template("Home/home.html", active_page="home")

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        npi = request.form["npi"]
        password = request.form["password"]
        user = authenticate_user(npi, password)
        if user:
            session['authenticated'] = True
            session['authenticated_npi'] = user['npi']
            session['authenticated_full_name'] = user['full_name']
            session['authenticated_role'] = user['role']
            return redirect(url_for('display_results' if user['role'].lower() == 'admin' else 'vote'))
        else:
            return render_template("Login/login.html", error_message="Invalid NPI or password")
    return render_template("Login/login.html", active_page="login")

@app.route("/results", methods=["GET"])
def display_results():
    if not session.get('authenticated', False):
        return redirect(url_for('login'))

    if session.get('authenticated_role', '').lower() != 'admin':
        return redirect(url_for('home'))

    winner = blockchain.get_winner()
    return render_template("Results/results.html", winner=winner, total_voters=len(blockchain.voters), is_vote_closed=blockchain.vote_closed, hash_rate=blockchain.get_average_hash_rate())

@app.route("/time_remaining", methods=["GET"])
def get_time_remaining():
    return jsonify(time_remaining(start_time, vote_duration))

@app.route("/blocks", methods=["GET"])
def display_blocks():
    blocks = [json.loads(str(block)) for block in blockchain.chain]
    return jsonify(blocks)

@app.route("/blocks/<int:hours>", methods=["GET"])
def get_blocks(hours):
    filtered_blocks = filter_data_based_on_time(blockchain, hours)
    blocks = [json.loads(str(block)) for block in filtered_blocks]
    return jsonify(blocks)

@app.route("/block/<string:hash_value>", methods=["GET"])
def display_block_by_hash(hash_value):
    block = blockchain.get_block_by_hash(hash_value)
    if block:
        return jsonify(json.loads(str(block)))
    return jsonify({"message": "Block not found"})

if __name__ == "__main__":
    app.run(debug=True)
