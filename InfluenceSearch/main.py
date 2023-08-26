import requests
from pymongo import MongoClient
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from googleapiclient.discovery import build

app = FastAPI()
templates = Jinja2Templates(directory="templates")

client = MongoClient("mongodb+srv://frozy:admin12@cluster0.v2thrmo.mongodb.net/?retryWrites=true&w=majority")
db = client['users']
collection = db['search']

DEVELOPER_KEY = 'AIzaSyDkwfihxOsnd2XRRyJOhQTNDS8TVSKVjik'
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def search_videos_by_keyword_category_and_subscriber_count(keyword, min_subscribers, max_subscribers, max_pages):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    next_page_token = None
    subscriber_counts = {}
    channel_icons = {}
    custom_urls = {}
    channel_videos = {}

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

    return channel_videos

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user_ip = request.client.host
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

    return templates.TemplateResponse("home.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
async def home_post(request: Request, search: str = Form(...)):
    user_ip = request.client.host
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
    "Search": search}

    inserted_data = collection.insert_one(data_to_insert)

    print(f"Data sent to database")
    
    sub_1 = 1000
    sub_2 = 1000000
    channel_data = search_videos_by_keyword_category_and_subscriber_count(search, sub_1, sub_2, 50)
    return templates.TemplateResponse("results.html", {"request": request, "videos": channel_data, "keyword": search})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/benefits", response_class=HTMLResponse)
async def benefits(request: Request):
    return templates.TemplateResponse("benefits.html", {"request": request})