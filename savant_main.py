# -*- coding: utf-8 -*-

import os

import flask
import json
from flask import request

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = os.environ['GOOGLE_CLIENT_SECRETS']

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works, but if you
# use this code in your application please replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.
app.secret_key = '\xb8S;\xbe;U,\x0c\xfd@E\xa0gK&\x07\x9cq\x05\x109\xf6p\x0b'

# topics for each collection category
TOPICS_TALK_SHOW = ['https://en.wikipedia.org/wiki/Entertainment', 'https://en.wikipedia.org/wiki/Telivision_program']
TOPICS_SPORTS = ['https://en.wikipedia.org/wiki/Sport']
TOPICS_MUSIC = ['https://en.wikipedia.org/wiki/Music']
TOPICS_TRAILERS = ['https://en.wikipedia.org/wiki/Trailer_(promotion)', 'https://en.wikipedia.org/wiki/Teaser_campaign']

COLLECTION_TALK_SHOW = { 'title' : 'Savant Talk Show', 'viewCountMin' : '1000000', 'viewDaysMax' : '7', 'topics' : TOPICS_TALK_SHOW, 
  'channels' : [], 'playlistId' : '', 'playlistItems' : [] }
COLLECTION_SPORTS = { 'title' : 'Savant Sports', 'viewCountMin' : '100000', 'viewDaysMax' : '7', 'topics' : TOPICS_SPORTS, 
  'channels' : [], 'playlistId' : '', 'playlistItems' : [] }
COLLECTION_MUSIC = { 'title' : 'Savant Music', 'viewCountMin' : '1000000', 'viewDaysMax' : '90', 'topics' : TOPICS_MUSIC, 
  'channels' : [], 'playlistId' : '', 'playlistItems' : [] }
COLLECTION_TRAILERS = { 'title' : 'Savant Trailers', 'viewCountMin' : '100000', 'viewDaysMax' : '90', 'topics' : TOPICS_TRAILERS, 
  'channels' : [], 'playlistId' : '', 'playlistItems' : [] }
  

@app.route('/myvideos')
def myvideos():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load the credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  client = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)
  
  return search_list(client,
    part='snippet', type='video',
    forMine=True, maxResults=50)

@app.route('/myplaylists')
def myplaylists():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load the credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  client = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)
  
  return playlists_list(client,
    part='snippet,contentDetails',
    mine=True, maxResults=50)

@app.route('/playlistvideos')
def playlistvideos():

  playlist_id = request.args.get('playlistid')
  viewCountMin = request.args.get('viewcountmin') if 'viewcountmin' in request.args else '10000'
  viewDaysMax = request.args.get('viewdaysmax') if 'viewdaysmax' in request.args else '10'

  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load the credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  client = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

  videos_ids  = []
  playlistitems_list_response = playlistitems_list(client, False,
    part='snippet,contentDetails',
    playlistId=playlist_id, maxResults=50)

  pl_items = playlistitems_list_response["items"]
  for pl_item in pl_items:
    videos_ids.append(pl_item["snippet"]["resourceId"]["videoId"])

  return query_videos_list(client, True, viewCountMin, viewDaysMax,
    part='snippet,contentDetails,statistics,status,topicDetails',
    id=",".join(videos_ids), maxResults=50)

@app.route('/playlistitems')
def playlistitems():

  playlist_id = request.args.get('playlistid')

  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load the credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  client = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

  return playlistitems_list(client,
    part='snippet,contentDetails',
    playlistId=playlist_id, maxResults=50)

@app.route('/mychannels')
def mychannels():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load the credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  client = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)
  
  return channels_list(client,
    part='snippet,contentDetails,statistics,topicDetails,status',
    mine=True, maxResults=50)

@app.route('/mysubscriptions')
def mysubscriptions():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load the credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  client = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)
  
  return subscriptions_list(client,
    part='snippet,contentDetails',
    mine=True, maxResults=50)

@app.route('/makecollections')
def makecollections():

  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load the credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  client = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)
  
  collections = topcollections(client, False)
  for collection in collections:
    # ensure playlist is available
    playlist = myplaylist(client, collection["title"], True)
    collection["playlistId"] = playlist["id"]

    for channel in collection["channels"]:
      for video in channel["videos"]:
        playlistitem_resource = {}
        playlistitem_resource["snippet"] = {}
        playlistitem_resource["snippet"]["playlistId"] = collection["playlistId"]
        playlistitem_resource["snippet"]["resourceId"] = {}
        playlistitem_resource["snippet"]["resourceId"]["kind"] = 'youtube#video'
        playlistitem_resource["snippet"]["resourceId"]["videoId"] = video["video_id"]

        playlist_item = playlist_items_insert(client, playlistitem_resource, False, part="snippet")
        playlistitem_resource["id"] = playlist_item["id"]
        playlistitem_resource["snippet"]["channelId"] = playlist_item["snippet"]["channelId"]
        playlistitem_resource["snippet"]["publishedAt"] = playlist_item["snippet"]["publishedAt"]
        playlistitem_resource["snippet"]["title"] = playlist_item["snippet"]["title"]
        
        collection["playlistItems"].append(playlistitem_resource)


  return flask.jsonify(collections=collections)

@app.route('/')
def index():

  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load the credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  client = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)
  
  return topcollections(client)

@app.route('/login')
def login():
  return flask.redirect('authorize')


@app.route('/authorize')
def authorize():
  # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow
  # steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
  authorization_url, state = flow.authorization_url(
      # This parameter enables offline access which gives your application
      # both an access and refresh token.
      access_type='offline',
      # This parameter enables incremental auth.
      include_granted_scopes='true')

  # Store the state in the session so that the callback can verify that
  # the authorization server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verify the authorization server response.
  state = flask.session['state']
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store the credentials in the session.
  # ACTION ITEM for developers:
  #     Store user's access and refresh tokens in your data store if
  #     incorporating this code into your real app.
  credentials = flow.credentials
  flask.session['credentials'] = {
      'token': credentials.token,
      'refresh_token': credentials.refresh_token,
      'token_uri': credentials.token_uri,
      'client_id': credentials.client_id,
      'client_secret': credentials.client_secret,
      'scopes': credentials.scopes
  }

  return flask.redirect(flask.url_for('index'))

def search_list(client, jsonify=True, **kwargs):
  response = client.search().list(
    **kwargs
  ).execute()

  return flask.jsonify(**response) if jsonify else response

def videos_list(client, jsonify=True, **kwargs):
  response = client.videos().list(
    **kwargs
  ).execute()

  return flask.jsonify(**response) if jsonify else response

def playlistitems_list(client, jsonify=True, **kwargs):
  response = client.playlistItems().list(
    **kwargs
  ).execute()

  return flask.jsonify(**response) if jsonify else response

def playlist_items_insert(client, resource, jsonify=True, **kwargs):
  response = client.playlistItems().insert(
    body=resource,
    **kwargs
  ).execute()

  return flask.jsonify(**response) if jsonify else response
  
def playlist_items_delete(client, jsonify=True, **kwargs):
  response = client.playlistItems().delete(
    **kwargs
  ).execute()

  return flask.jsonify(**response) if jsonify else response

def playlists_list(client, jsonify=True, **kwargs):
  response = client.playlists().list(
    **kwargs
  ).execute()

  return flask.jsonify(**response) if jsonify else response

def playlists_insert(client, resource, jsonify=True, **kwargs):
  response = client.playlists().insert(
    body=resource,
    **kwargs
  ).execute()

  return flask.jsonify(**response) if jsonify else response

def playlists_delete(client, jsonify=True, **kwargs):
  response = client.playlists().delete(
    **kwargs
  ).execute()

  return flask.jsonify(**response) if jsonify else response

def channels_list(client, jsonify=True, **kwargs):
  response = client.channels().list(
    **kwargs
  ).execute()

  return flask.jsonify(**response) if jsonify else response

def subscriptions_list(client, jsonify=True, **kwargs):
  response = client.subscriptions().list(
    **kwargs
  ).execute()

  return flask.jsonify(**response) if jsonify else response

def query_videos_list(client, jsonify=True, viewCountMin=10000, viewDaysMax=10, **kwargs):
  import dateutil.parser
  from datetime import datetime, timedelta

  videos_list_response = videos_list(client, False, **kwargs)
  v_items = videos_list_response["items"]

  videos_items = []
  for v_item in v_items:
    view_count = v_item["statistics"]["viewCount"]
    if int(view_count) < int(viewCountMin):
      continue

    published_time = dateutil.parser.parse(v_item["snippet"]["publishedAt"])
    allowed_time = datetime.now() - timedelta(days=int(viewDaysMax))
    if published_time.replace(tzinfo=None) < allowed_time:
      continue
    
    videos_items.append(v_item)

  videos_list_response["items"] = videos_items
  return flask.jsonify(videos_list_response)  if jsonify else videos_list_response


def myplaylist(client, playlistName, recreate=False): 
  # get playlist info
  playlists_list_response = playlists_list(client, False,
    part='snippet,contentDetails',
    mine=True, maxResults=50)

  # match name
  playlist = next((pl for pl in playlists_list_response["items"] if pl["snippet"]["title"] == playlistName), None)

  if recreate and playlist: 
    playlists_delete(client, False, id=playlist["id"])
    playlist = None
    
  if not playlist: 
    playlist_resource = {}
    playlist_resource["snippet"] = {}
    playlist_resource["snippet"]["title"] = playlistName
    playlist_resource["status"] = {}      
    playlist_resource["status"]["privacyStatus"] = "private"
    playlist = playlists_insert(client, playlist_resource, False, part="snippet,status") 

  return playlist

def playlists_from_channels(client, channelId, viewCountMin, viewDaysMax):
  # show playlist summary if need be
  playlists  = []
  playlists_list_response = playlists_list(client, False,
    part='snippet,contentDetails',
    channelId=channelId, maxResults=50)
  p_items = playlists_list_response["items"]

  for p_item in p_items:
    playlist = {}
    playlist["playlist_id"] = p_item["id"]
    playlist["title"] = p_item["snippet"]["title"]

    videos_ids  = []
    playlistitems_list_response = playlistitems_list(client, False,
      part='snippet,contentDetails',
      playlistId=playlist["playlist_id"], maxResults=50)

    pl_items = playlistitems_list_response["items"]
    for pl_item in pl_items:
      videos_ids.append(pl_item["snippet"]["resourceId"]["videoId"])

    query_videos_list_response = query_videos_list(client, False, 
      viewCountMin, viewDaysMax,
      part='snippet,contentDetails,statistics,status,topicDetails',
      id=",".join(videos_ids), maxResults=50)
    
    videos = []
    v_items = query_videos_list_response["items"]
    for v_item in v_items:
      video = {}
      video["video_id"] = v_item["id"]
      video["title"] = v_item["snippet"]["title"]
      video["published_at"] = v_item["snippet"]["publishedAt"]
      video["view_count"] = v_item["statistics"]["viewCount"]
      videos.append(video)

    playlist["videos"] = videos
    playlists.append(playlist)

  return playlists

  
def channel_topics_list(client, channelId):

  # get channel info
  channels_list_response = channels_list(client, False,
    part='snippet,topicDetails',
    id=channelId, maxResults=50)

  # collect channel topics
  channel = next((c for c in channels_list_response["items"] if "topicDetails" in c), None)   
  
  return channel["topicDetails"]["topicCategories"] if channel else None


def topcollections(client, jsonify=True):

  collections = [COLLECTION_TALK_SHOW, COLLECTION_SPORTS, COLLECTION_MUSIC] 

  # get subscriptions info
  subscriptions_list_response = subscriptions_list(client, False,
    part='snippet',
    mine=True, maxResults=50)
  items = subscriptions_list_response["items"]

  # cycle through channel info 
  for item in items:
    channel = {}
    channel["title"] = item["snippet"]["title"]
    channel["channel_id"] = item["snippet"]["resourceId"]["channelId"]
    # channel["published_at"] = item["snippet"]["publishedAt"]
    channel["topics"] = channel_topics_list(client, channel["channel_id"])

    # get the appropriate collection
    # TODO: Check Subset  
    collection = next((c for c in collections if not set(c["topics"]).isdisjoint(channel["topics"])), None) 
    if not collection:
      continue

    # search for all videos of channel after certain date with decreasing views order
    from datetime import datetime, timedelta
    allowed_time = datetime.utcnow() - timedelta(days=int(collection["viewDaysMax"]))
    published_after = allowed_time.replace(microsecond=0).isoformat() + "Z"
    search_list_response = search_list(client, False,
        part='snippet', channelId=channel["channel_id"],
        publishedAfter=published_after, order='viewCount', maxResults=50)

    video_ids = []
    vi_items = search_list_response["items"]
    for vi_item in vi_items:
      if "videoId" in vi_item["id"]:
        video_ids.append(vi_item["id"]["videoId"])

    # remove videos with views lower than threshold
    query_videos_list_response = query_videos_list(client, False, 
      collection["viewCountMin"], collection["viewDaysMax"],
      part='snippet,statistics',
      id=",".join(video_ids), maxResults=50)
    
    videos = []
    v_items = query_videos_list_response["items"]
    for v_item in v_items:
      video = {}
      video["video_id"] = v_item["id"]
      video["title"] = v_item["snippet"]["title"]
      
      video["published_at"] = v_item["snippet"]["publishedAt"]
      video["view_count"] = v_item["statistics"]["viewCount"]

      # video["channel_title"] = item["snippet"]["channelTitle"] if "channelTitle" in item["snippet"] else ""
      video["channel_id"] = item["snippet"]["channelId"] if "channelId" in item["snippet"] else ""
      videos.append(video)

    channel["videos"] = videos
    
    # add the channel to the collection
    collection["channels"].append(channel)

  return flask.jsonify(collections=collections) if jsonify else collections


if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification. When
  # running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  app.run('localhost', 8080, debug=True)
