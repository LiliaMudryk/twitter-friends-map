'''
Web application to see location of user's twitter friends.
'''
from geopy.geocoders import Nominatim
import requests
import folium
from flask import Flask, render_template, request

app = Flask(__name__)

def get_friens_information(acct:str,bearer_token:str) -> dict:
    """
    Uses bearer token and screen name to get information about
    friends on twitter of specified user.
    """
    twitter_url = 'https://api.twitter.com/1.1/friends/list.json'
    if len(acct) < 1:
        return
    search_headers = {
        'Authorization' : 'Bearer {}'.format(bearer_token),
        'content-type' : 'application/json'
    }
    search_params = {
        'screen_name' : acct,
        'count' : 10
    }
    response = requests.get(twitter_url, headers=search_headers ,params= search_params)
    json_response = response.json()
    friends = {}
    for user in json_response['users']:
        name = user['screen_name']
        location = user['location']
        if location != '':
            friends[location] = name
        if len(friends) == 10:
            break
    return friends


def generate_map(friends_info: dict):
    """
    Generates map, where markers are location of twitter friends of the specified user.
    Saves the map in folder templates with name 'friends_map.html'
    """
    friends_map = folium.Map()
    geolocator = Nominatim(user_agent="user")
    for i in friends_info:
        location = geolocator.geocode(i)
        friends_map.add_child(folium.Marker(location=[location.latitude,location.longitude],
                                            popup=friends_info[i]+',\n'+i))
    friends_map.save('templates/friends_map.html')

@app.route("/")
def index():
    '''
    Returns main page of web application.
    '''
    return render_template("index.html")

@app.route("/generate_map", methods=["POST"])
def build_map():
    '''
    Returns map with markers of friends location.
    If Keyerror returns 'failure.html'
    '''
    if not (request.form.get('screen_name') or request.form.get('bearer_token')):
        return render_template("failure.html")
    try:
        user_name = request.form.get('screen_name')
        token = request.form.get('bearer_token')
        generate_map(get_friens_information(user_name,token))
        return render_template('friends_map.html')
    except KeyError:
        return render_template("failure.html")

if __name__ == "__main__":
    app.run(debug=False)
