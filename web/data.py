from pymongo import MongoClient
import requests

class Data:
    def __init__(self, flask_request):
        self.client = MongoClient() #your database link
        self.db = self.client['users']
        self.collection = self.db['search']
        self.collection1 = self.db['visitors']
        self.collection2 = self.db['email_data']
        self.collection3 = self.db['influencers_database']

        self.user_ip = flask_request.remote_addr
        self.user_agent = flask_request.headers.get("User-Agent")
        self.referrer = flask_request.headers.get("Referer")

        url = f"http://ip-api.com/json/{self.user_ip}"
        response = requests.get(url)
        data = response.json()

        self.country = data.get("country")
        self.region = data.get("regionName")
        self.city = data.get("city")

        self.base_data = {
            "User Ip": self.user_ip,
            "User agent": self.user_agent,
            "Referer": self.referrer,
            "Country": self.country,
            "Region": self.region,
            "City": self.city,
        }

