from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from data import Data

class Search:
    def __init__(self,flask_request):
        self.db = Data(flask_request)
        self.DEVELOPER_KEY = "" #your youtube v3 api
        self.YOUTUBE_API_SERVICE_NAME = "youtube"
        self.YOUTUBE_API_VERSION = "v3"

    def Youtube(self, keyword, min_subscribers, max_subscribers, max_pages):
        youtube = build(
            self.YOUTUBE_API_SERVICE_NAME,
            self.YOUTUBE_API_VERSION,
            developerKey=self.DEVELOPER_KEY,
        )

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
                    pageToken=next_page_token,
                ).execute()

                video_ids = [item["id"]["videoId"] for item in search_response["items"]]
                channel_ids = [item["snippet"]["channelId"] for item in search_response["items"]]

                channel_response = youtube.channels().list(
                    part="snippet, statistics",
                    id=",".join(channel_ids),
                    maxResults=1000,
                ).execute()

                for channel in channel_response["items"]:
                    channel_id = channel["id"]
                    subscriber_counts[channel_id] = int(channel["statistics"]["subscriberCount"])
                    channel_icons[channel_id] = channel["snippet"]["thumbnails"]["default"]["url"]

                    if "customUrl" in channel["snippet"]:
                        custom_urls[channel_id] = channel["snippet"]["customUrl"]
                    else:
                        custom_urls[channel_id] = None

                    influencer_data = {
                        "keyword": keyword,
                        "channel_name": channel["snippet"]["title"],
                        "subscriber_count": subscriber_counts[channel_id],
                        "channel_url": f"https://www.youtube.com/{channel_id}",
                        "channel_image": channel_icons[channel_id],
                        "custom_url": custom_urls[channel_id],
                    }

                    self.db.collection3.insert_one(influencer_data)

                video_response = youtube.videos().list(
                    part="snippet, statistics",
                    id=",".join(video_ids),
                    maxResults=50,
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
                                "videos": [],
                            }
                        channel_videos[channel_id]["videos"].append(
                            {
                                "video_title": video["snippet"]["title"],
                                "video_id": video["id"],
                            }
                        )

                next_page_token = search_response.get("nextPageToken")
                if not next_page_token:
                    break

        except HttpError as e:
            if e.resp.status == 403 and "quota" in str(e):
                print("API quota exceeded. Redirecting to /error.")
                return None


        return channel_videos
