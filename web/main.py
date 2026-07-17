import os
import requests
from pymongo import MongoClient
from flask import Flask, render_template, request, redirect
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)

DEVELOPER_KEY = 'AIzaSyDkwfihxOsnd2XRRyJOhQTNDS8TVSKVjik'
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

client = MongoClient("mongodb://frozy:admin12@ac-puc2pbz-shard-00-00.v2thrmo.mongodb.net:27017,ac-puc2pbz-shard-00-01.v2thrmo.mongodb.net:27017,ac-puc2pbz-shard-00-02.v2thrmo.mongodb.net:27017/?ssl=true&replicaSet=atlas-fle5nk-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client['users']
collection = db['search']
collection1 = db['visitors']
collection2 = db['email_data']
collection3 = db['influencers_database']

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def search_videos_by_keyword_category_and_subscriber_count(keyword, min_subscribers, max_subscribers, max_pages):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    next_page_token = None
    subscriber_counts = {}
    channel_icons = {}
    custom_urls = {}
    channel_videos = {}

    try:
        for i in range(max_pages):
            search_response = youtube.search().list(
                q=keyword,
                type="video",
                part="id, snippet",
                maxResults=50,
                regionCode="US",
                pageToken=next_page_token
            ).execute()

            video_ids = [item["id"]["videoId"] for item in search_response["items"]]
            channel_ids = [item["snippet"]["channelId"] for item in search_response["items"]]

            channel_response = youtube.channels().list(
                part="snippet, statistics",
                id=",".join(channel_ids),
                maxResults=1000
            ).execute()

            for channel in channel_response["items"]:
                channel_id = channel["id"]
                subscriber_counts[channel_id] = int(channel["statistics"]["subscriberCount"])
                channel_icons[channel_id] = channel["snippet"]["thumbnails"]["default"]["url"]

                if "customUrl" in channel["snippet"]:
                    custom_urls[channel_id] = channel["snippet"]["customUrl"]
                else:
                    custom_urls[channel_id] = None

                # Create a document for the influencer
                influencer_data = {
                    "keyword": keyword,
                    "channel_name": channel["snippet"]["title"],
                    "subscriber_count": subscriber_counts[channel_id],
                    "channel_url": f"https://www.youtube.com/{channel_id}",
                    "channel_image": channel_icons[channel_id],
                    "custom_url": custom_urls[channel_id]
                }

                # Insert the influencer data into the database
                collection3.insert_one(influencer_data)

            video_response = youtube.videos().list(
                part="snippet, statistics",
                id=",".join(video_ids),
                maxResults=50
            ).execute()

            for video in video_response["items"]:
                channel_id = video["snippet"]["channelId"]
                if min_subscribers <= subscriber_counts[channel_id] <= max_subscribers:
                    if channel_id not in channel_videos:
                        channel_videos[channel_id] = {
                            "channel_title": video["snippet"]["channelTitle"],
                            "subscriber_count": subscriber_counts[channel_id],
                            "channel_icon": channel_icons[channel_id],
                            "custom_url": custom_urls[channel_id],
                            "videos": []
                        }
                    channel_videos[channel_id]["videos"].append({
                        "video_title": video["snippet"]["title"],
                        "video_id": video["id"],
                    })

            next_page_token = search_response.get("nextPageToken")
            if not next_page_token:
                break

    except HttpError as e:
        if e.resp.status == 403 and "quota" in str(e):
            print("API quota exceeded. Redirecting to /error.")
            return None

    return channel_videos


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        search = request.form['search']
        user_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        referrer = request.headers.get('Referer')
        url = f"http://ip-api.com/json/{user_ip}"
        response = requests.get(url)
        data = response.json()
        country = data.get("country")
        region = data.get("regionName")
        city = data.get("city")

        print(user_ip)
        print(user_agent)
        print(referrer)
        print(country)
        print(region)
        print(city)
        print(search)

        data_to_insert = {
            "User Ip": user_ip,
            "User agent": user_agent,
            "Referer": referrer,
            "Country": country,
            "Region": region,
            "City": city,
            "Search": search
        }

        inserted_data = collection.insert_one(data_to_insert)

        print(f"Data sent to database")

        sub_1 = 1000
        sub_2 = 1000000

        # Retrieve data from the API
        channel_data = search_videos_by_keyword_category_and_subscriber_count(search, sub_1, sub_2, 50)

        if channel_data is None:
            return redirect("/email")

        return render_template("results.html", videos=channel_data, keyword=search)

    else:
        user_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        referrer = request.headers.get('Referer')
        url = f"http://ip-api.com/json/{user_ip}"
        response = requests.get(url)
        data = response.json()
        country = data.get("country")
        region = data.get("regionName")
        city = data.get("city")

        print(user_ip)
        print(user_agent)
        print(referrer)
        print(country)
        print(region)
        print(city)

        data_to_insert = {
            "User Ip": user_ip,
            "User agent": user_agent,
            "Referer": referrer,
            "Country": country,
            "Region": region,
            "City": city,
        }

        inserted_data = collection.insert_one(data_to_insert)
        return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/benefits")
def benefits():
    return render_template("benefits.html")

@app.route("/email", methods=['GET', 'POST'])
def error():
    if request.method == 'POST':
        addr = request.form['addr']
        user_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        referrer = request.headers.get('Referer')
        url = f"http://ip-api.com/json/{user_ip}"
        response = requests.get(url)
        data = response.json()
        country = data.get("country")
        region = data.get("regionName")
        city = data.get("city")

        print("User Ip:", user_ip)
        print("User Agent:", user_agent)
        print("Referer:", referrer)
        print("Country:",country)
        print("Region:",region)
        print("City:", city)
        print("Email:", addr)

        data_to_insert = {
            "User Ip": user_ip,
            "User agent": user_agent,
            "Referer": referrer,
            "Country": country,
            "Region": region,
            "City": city,
            "Email": addr
        }

        inserted_data = collection2.insert_one(data_to_insert)

        return render_template("red.html")

    return render_template("error_traffic.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1900)
