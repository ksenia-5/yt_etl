import requests
import json

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='./.env')

API_KEY = os.getenv('API_KEY')

YT_HANDLE = 'wgsn'

MAX_RESULTS = 50


def get_playlist_id() -> str:
    url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={YT_HANDLE}&key={API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()

        channel_items = data.get('items')[0]
        channel_playlist_id = channel_items.get('contentDetails').get('relatedPlaylists').get('uploads')
        return channel_playlist_id
    
    except requests.exceptions.RequestException as e:
        raise e



def get_playlist_items(playlist_id : str) -> list:

    video_id_list = []
    page_token = None
    base_url = f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={MAX_RESULTS}&playlistId={playlist_id}&key={API_KEY}'    

    try:
        while True:
            url = base_url
            if page_token:
                url += f"&pageToken={page_token}"

            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            playlist_items = data.get('items', [])
            
            new_video_ids = [pi.get('contentDetails').get('videoId') for pi in playlist_items]
            video_id_list += new_video_ids

            page_token = data.get('nextPageToken', None)
            
            if not page_token:
                break
        
        return video_id_list
    
    except requests.exceptions.RequestException as e:
        raise e
    

def extract_video_data(video_id_list):
    
    extracted_data = []

    def batch_list(video_id_list, batch_size):
        for i in range(0, len(video_id_list), batch_size):
            yield video_id_list[i : i + batch_size]


    try:
        for batch in batch_list(video_id_list, MAX_RESULTS):
            video_ids_str = ','.join(batch)
            url = f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id={video_ids_str}&key={API_KEY}'

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            for item in data.get('items',[]):
                video_id = item.get('id')
                snippet = item.get('snippet')
                content_details = item.get('contentDetails')
                statistics = item.get('statistics')

                video_data = {
                    'video_id': video_id,
                    'title': snippet.get('title'),
                    'description': snippet.get('description'),
                    'published_at': snippet.get('publishedAt'),
                    'duration': content_details.get('duration'),
                    'view_count': statistics.get('viewCount', None),
                    'like_count': statistics.get('likeCount', None),
                    'comment_count': statistics.get('commentCount', None),
                    'has_caption': content_details.get('caption')
                }

                extracted_data.append(video_data)
        return extracted_data

    except requests.exceptions.RequestException as e:
        raise e
    

if __name__ == '__main__':
    playlist_id = get_playlist_id()
    video_id_list = get_playlist_items(playlist_id)
    video_data = extract_video_data(video_id_list)
