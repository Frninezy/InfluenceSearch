import os
from data import Data
from search import Search
from pymongo import MongoClient
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_data = Data(request)
        find = Search(request)
        search_term = request.form['search']

        user_data.base_data["Search"] = search_term
        user_data.collection.insert_one(user_data.base_data)

        sub_1, sub_2 = 1000, 3000
        channel_data = find.Youtube(search_term, sub_1, sub_2, 2)

        if channel_data is None:
            return redirect("/email")

        return render_template("results.html", videos=channel_data, keyword=search_term)
    else:
        return render_template("home.html")


@app.route("/email", methods=['GET', 'POST'])
def error():
    if request.method == 'POST':
        user_data = Data(request)
        addr = request.form['addr']
        user_data.base_data["Email"] = addr
        user_data.collection2.insert_one(user_data.base_data)
        return render_template("red.html")

    return render_template("error_traffic.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/benefits")
def benefits():
    return render_template("benefits.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1900)
