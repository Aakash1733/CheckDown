from flask import Flask, request, jsonify,render_template,send_file
import requests
import datetime
from google.cloud import datastore
from google.cloud.datastore import query
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"


app = Flask(__name__)
import csv
import tkinter as tk
from tkinter import filedialog

# ...
@app.route('/',methods=['POST','GET'])
def home():
    return render_template('index.html')
@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")
@app.route("/download", methods=["GET"])
def download_report():
    # Retrieve all reported websites from the Cloud Datastore
    client = datastore.Client()
    query = client.query(kind="Website")
    reported_websites = list(query.fetch())

    # Generate a CSV file
    csv_data = []
    headers = ["URL", "Report Count", "Last Reported Time"]
    csv_data.append(headers)

    for website in reported_websites:
        url = website.key.name
        report_count = website.get("report_count")
        last_reported_time = website.get("last_reported_time")

        row = [url, report_count, last_reported_time]
        csv_data.append(row)

    # Prompt the user to choose the file path and filename
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension=".csv")

    if not file_path:
        return "No file selected."

    # Create the CSV file
    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)

    # Return the CSV file as a download
    return send_file(file_path, as_attachment=True)



@app.route("/check", methods=["GET"])
def check_website():
    url = request.args.get("url")
    if url:
        # Add your website checking logic here
        is_website_up = check_website_status(url)
        if is_website_up:
            message = "The website is up and running."
            recent_record = ""
        else:
            message = "The website is down or unavailable."

            # Fetch the most recent record from the backend database
            recent_record = get_most_recent_record(url)
    else:
        message = "Invalid URL provided."
        recent_record = ""

    response = {
        "message": message+recent_record
    }

    return jsonify(response)

def get_most_recent_record(url):
    # Fetch the most recent record from the backend database
    
    client = datastore.Client()
    try:
        entity_key = client.key("Website", url)
        entity = client.get(entity_key)
        if entity:
            # If entity exists, increment the report/views count and update the last reported time
            a=entity["report_count"]
            b=entity["last_reported_time"]
            return "Hola ! "+a+"people have tried to access the website . The most recent request was made at "+b
    except:
        return ""



# ... Rest of the code ...



@app.route("/report", methods=["GET"])
def report_website():
    url = request.args.get("url")
    if url:
        # Add your website reporting logic here
        is_website_up = check_website_status(url)
        current_time = datetime.datetime.now()

        # Store the website information in Cloud Datastore
        client = datastore.Client()

        # Create a new entity with the URL as the key
        entity_key = client.key("Website", url)
        entity = client.get(entity_key)

        if entity:
            # If entity exists, increment the report/views count and update the last reported time
            report_count = entity.get("report_count", 0) + 1
            entity["report_count"] = report_count
            entity["last_reported_time"] = current_time
        else:
            # If entity doesn't exist, set the initial report/views count
            entity = datastore.Entity(key=entity_key)
            entity["report_count"] = 1
            entity["last_reported_time"] = current_time

        # Save the entity in Cloud Datastore
        client.put(entity)

        # Save the entity in Cloud Datastore
  

        message = "Thank you for reporting the website."
    else:
        message = "Invalid URL provided."

    return jsonify({"message": message})

def check_website_status(url):
    # Add your website checking logic here using the requests library or any other method
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False

if __name__ == "__main__":
    app.run(host='127.0.0.1',port=8080,debug=True)
