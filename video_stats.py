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
        print(channel_playlist_id)
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
                print(url)
            

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

if __name__ == '__main__':
    playlist_id = get_playlist_id()
    get_playlist_items(playlist_id)

