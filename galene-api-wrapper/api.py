import requests
import os
from dotenv import load_dotenv

class GaleneAPI():
    '''An API wrapper for Galène'''

    load_dotenv()

    username = os.getenv('API_ADMIN_LOGIN')
    password = os.getenv('API_ADMIN_PASSWORD')

    def __init__(self, url="http://localhost", location="/galene-api/v0/"):
        '''Initialize GaleneAPI instance with server url (default is localhost) 
        and API endpoints path (default is /galene-api/v0/, as per the official Galène docs)'''
        self.url = url
        self.location = location
        self.api_path = url + location

    def getstats(self):
        '''Gets stats, returns a JSON (TODO: explain further)'''
        req = requests.get(self.api_path + ".stats", auth=(self.username, self.password))
        return req.json()

    def list_groups(self):
        '''The .groups galene API endpoint exists in docs but seems to return a 404 here, idk why'''
        req = requests.get(self.api_path + ".groups")
        return req.json()
