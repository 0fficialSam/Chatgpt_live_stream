import os
import openai
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import time
import json

openai.api_key = 'todo'

scopes  = ["https://www.googleapis.com/auth/youtube.force-ssl"]

client_secret_file = "sam_secret.json"

flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
creds = flow.run_local_server(port=0)
yt = googleapiclient.discovery.build("youtube", "v3", credentials=creds)


#get live_stream_video_id
def get_live_stream(yt):
    request = yt.liveBroadcasts().list(part='id,snippet',broadcastStatus='active',broadcastType='all')
    response = request.execute()
    if response['items']:
        live_video_id = response['items'][0]['id']
        return live_video_id
    else:
        return None
    
#get chat_id
def get_live_chat_id(yt,live_video_id):
    request = yt.videos().list(part='liveStreamingDetails',id=live_video_id)
    response = request.execute()
    live_chat_id = response['items'][0]['liveStreamingDetails']['activeLiveChatId']
    return live_chat_id

#get chat msgs
def get_live_chat(yt,live_chat_id):
    request = yt.liveChatMessages().list(liveChatId=live_chat_id, part='snippet,authorDetails')
    response = request.execute()
    return response['items']

#post msg back to chat
def post_msg(yt,live_chat_id, msg):
    request = yt.liveChatMessages().insert(
        part='snippet',
        body={
            'snippet': {
                'liveChatId': live_chat_id,
                'type': 'textMessageEvent',
                'textMessageDetails': {
                    'messageText': message
                }
            }
        }
    )
    reponse = request.execute()
    return reponse

live_video_id = get_live_stream(yt)

live_chat_id= get_live_chat_id(yt, live_video_id)

while True:
    messages = get_live_chat(yt, live_chat_id)
    for message in messages:
        user_message = message['snippet']['textMessageDetails']['messageText']
        if 'hey dodo' in user_message.lower():
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                prompt=user_message,
                max_tokens=50
            )
            bot_message = response.choices[0].text.strip()
            post_msg(yt, live_chat_id, bot_message)
    time.sleep(5)


