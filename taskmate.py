import json
from apiclient.discovery import build_from_document, build
import httplib2
import random
import requests

from oauth2client import client
from oauth2client.client import OAuth2WebServerFlow

from flask import Flask, render_template, session, request, redirect, url_for, abort

CLIENT_ID = "805075416684-sm8ktm9sel14r7fv42tocdmpsk423fni.apps.googleusercontent.com"
CLIENT_SECRET = 'p_4wg243g0N5seeG9sgxj1fz'
YO_API_TOKEN = 'b0651284-6164-485d-99ee-fa95a8f4f13a'


app = Flask(__name__)


@app.route('/login')
def login():
  flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope='https://www.googleapis.com/auth/youtube',
    redirect_uri='http://localhost:8000/oauth2callback',
    approval_prompt='force',
    access_type='offline')

  auth_uri = flow.step1_get_authorize_url()
  return redirect(auth_uri)

@app.route('/signout')
def signout():
  del session['credentials']
  session['message'] = "You have logged out"

  return redirect(url_for('index'))

@app.route('/oauth2callback')
def oauth2callback():
  code = request.args.get('code')
  if code:
    # exchange the authorization code for user credentials
    flow = OAuth2WebServerFlow(CLIENT_ID,
      CLIENT_SECRET,
      "https://www.googleapis.com/auth/youtube")
    flow.redirect_uri = request.base_url
    try:
      credentials = flow.step2_exchange(code)
    except Exception as e:
      print "Unable to get an access token because ", e.message

    # store these credentials for the current user in the session
    # This stores them in a cookie, which is insecure. Update this
    # with something better if you deploy to production land
    session['credentials'] = credentials.to_json()

  return redirect(url_for('index'))

@app.route('/')
def index():
  if 'credentials' not in session:
    return redirect(url_for('login'))

  credentials = session['credentials']

  http = httplib2.Http()
  http = credentials.authorize(http)

  youtube = build("youtube", "v3", http=http)
  playlists = youtube.playlists().list(
    part="id,snippet",
    mine=True
  ).execute()
  return render_template("index.html", playlists=playlists)

@app.route('/yo')
def yo():
	template_values = {}
	return render_template('yo.html', values=template_values)

@app.route('/yo/send')
def yo_request():
	username = request.args.get('username')
	template_values = {'username':username}
	requests.post("http://api.justyo.co/yo/", data={'api_token': YO_API_TOKEN,'username':username})
	return render_template('yo.html', values=template_values)

if __name__ == "__main__":
	app.secret_key = 'development'
	app.run(debug=True, port=8000)