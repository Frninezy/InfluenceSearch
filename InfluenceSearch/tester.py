import googleapiclient.errors
import googleapiclient.discovery
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DEVELOPER_KEY = 'AIzaSyDkwfihxOsnd2XRRyJOhQTNDS8TVSKVjik'
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def search_videos_by_keyword_category_and_subscriber_count(keyword, min_subscribers, max_subscribers, max_pages):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    next_page_token = None
    channel_urls = []
    for i in range(max_pages):
        # Search for videos with the keyword in the fashion category and from the United States
        search_response = youtube.search().list(
            q=keyword,
            type="video",
            part="id, snippet",
            maxResults=50,
            regionCode="US",
            pageToken=next_page_token
        ).execute()

        # Get the channel IDs of the search results
        channel_ids = [item["snippet"]["channelId"] for item in search_response["items"]]

        # Retrieve information about the channels with the retrieved channel IDs
        channel_response = youtube.channels().list(
            part="snippet, statistics",
            id=",".join(channel_ids),
            maxResults=1000
        ).execute()

        for channel in channel_response["items"]:
            channel_id = channel["id"]
            subscriber_count = int(channel["statistics"]["subscriberCount"])

            if min_subscribers <= subscriber_count <= max_subscribers:
                if "customUrl" in channel["snippet"]:
                    custom_url = f'https://www.youtube.com/c/{channel["snippet"]["customUrl"]}'
                else:
                    custom_url = None

                regular_url = f'https://www.youtube.com/channel/{channel_id}'
                channel_urls.append((custom_url, regular_url))

        next_page_token = search_response.get("nextPageToken")
        if not next_page_token:
            break

    return channel_urls

# Example usage
keyword = "hacking"
min_subscribers = 10000
max_subscribers = 500000
max_pages = 3
urls = search_videos_by_keyword_category_and_subscriber_count(keyword, min_subscribers, max_subscribers, max_pages)
for custom_url, regular_url in urls:
    if custom_url:
        print("Custom URL:", custom_url)
    print("Regular URL:", regular_url)
    print()
