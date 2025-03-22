import os
import requests
from yt_dlp import YoutubeDL

class Track:
    def __init__(self, name, artists):
        self.name = name
        self.artists = artists

def append_tracks(tracks, playlist_id, access_token, offset):
    url_following = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={offset}&limit=100&fields=items(track(name,artists(name))),next'
    response_url_following = requests.get(url=url_following, headers={'Authorization': f'Bearer {access_token}'})

    tracks += [Track(**item['track']) for item in response_url_following.json()['items']]

    if(response_url_following.json()['next'] != None): 
        offset += 100
        append_tracks(tracks, playlist_id, access_token, offset)

    return tracks

    
def download_song(track, folder_name):

    ydl_opts = {
        'postprocessors': [
            {
                'preferredcodec': 'mp3',
                'preferredquality': '192',
                'key': 'FFmpegExtractAudio',
            },
            {'key' : 'FFmpegMetadata'}
        ],
        'age_limit': 25,
        'addmetadata':True,
        'format': 'bestaudio/best',
        'outtmpl': f'/home/cuarcuar/Downloads/songs/{folder_name}/{track.name}',
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'ytsearch:{track.name} song, by {track.artists[0]["name"]}'])
            print('Done.\n')
            
    except Exception as error:
        print(f'An error occurred: {error}\n')

if __name__ == "__main__":

    while True:

        folder_name = input('\nTo start, type folder name, or \'exit\' to quit program: ')
        if(folder_name == 'exit'):
            print('\nExiting...')
            break

        if(folder_name in os.listdir('/home/cuarcuar/Downloads/songs/')): saved_tracks = list(map(lambda song: song[:-4], os.listdir(f'/home/cuarcuar/Downloads/songs/{folder_name}')))
        
        playlist_id = input('\nSpotify playlist id: ')
        print('\nLoading...')

        url_get_token = 'https://accounts.spotify.com/api/token'
        data_get_token = f'grant_type=client_credentials&client_id=c2c95a16f168413f9bced8544b491822&client_secret={os.environ["SPOTY_SECRET"]}'

        response_get_token = requests.post(url=url_get_token, data=data_get_token, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if(response_get_token.status_code != 200):
            print('\nSomething went wrong in retrieving the token from spoty!')
            break

        access_token = response_get_token.json()['access_token']
        print(f'\nYour access token is: {access_token}')
        
        url_get_songs = f'https://api.spotify.com/v1/playlists/{playlist_id}?fields=tracks.items(track(name,artists(name))),tracks.next'

        response_playlist = requests.get(url=url_get_songs, headers={'Authorization': f'Bearer {access_token}'})
        if(response_playlist.status_code != 200):
            print('\nSomething went wrong in retrieving the playlist from spoty!')
            break

        tracks = [ Track(**item['track']) for item in response_playlist.json()['tracks']['items'] ]

        if(response_playlist.json()['tracks']['next'] != None): tracks = append_tracks(tracks, playlist_id, access_token, 100)

        filtered_tracks = list(filter(lambda track: track.name not in saved_tracks, tracks))

        for track in filtered_tracks:
            download_song(track, folder_name)