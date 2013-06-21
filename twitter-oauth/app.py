'''
A quick little app that will use Twitter OAuth to get an access token for a particular user

Python 2.7
pip install Flask-OAuth

http://pythonhosted.org/Flask-OAuth/

'''

from flask import Flask, request, session, url_for, redirect, render_template
from flask_oauth import OAuth
import json
import os

# Load consumer key/secret
with open('secret.json') as f: secret = json.loads(f.read())

print secret['consumer_key']
print secret['consumer_secret']

# OAuth setup
oauth = OAuth()
twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key=secret['consumer_key'],
    consumer_secret=secret['consumer_secret']
)

# Flask setup
app = Flask('twitter-oauth')
# Need a secret key for session
app.secret_key = os.urandom(24) 

# Token getter
@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')

# Login handler - just authorize with Twitter and let the callback do the rest.
@app.route('/login')
def login():
    return twitter.authorize(callback=url_for('oauth_cb', next=None))

@app.route('/oauth_cb')
@twitter.authorized_handler
def oauth_cb(resp):
    if resp is None:
        # Denied
        return redirect(url_for('login_denied'))
    
    session['twitter_token'] = (resp['oauth_token'], resp['oauth_token_secret'])
    session['twitter_user'] = resp['screen_name']
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('twitter_token', None)
    session.pop('twitter_user', None)
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html', token=session.get('twitter_token'), user=session.get('twitter_user'))

@app.route('/login_denied')
def login_denied():
   return render_template('login_denied.html')


if __name__ == '__main__':
   app.debug = True
   app.run()

