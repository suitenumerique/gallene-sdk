import requests

class GaleneAPI():
    '''An API wrapper for Galène'''

    username = ""
    password = ""

    def __init__(self, url="localhost", location="/galene-api/v0/"):
        '''Initialize GaleneAPI instance with server url (default is localhost) 
        and API endpoints path (default is /galene-api/v0/, as per the official Galène docs)'''
        self.url = url
        self.location = location
        self.api_path = url + location

    def getstats():
        '''Gets stats, returns a JSON (TODO: explain further)'''
        req = requests.get(self.api_path + ".stats", auth=(username, password))
        return req.json()

    def list_groups():
        '''Lists groups, returns a JSON (TODO: explain further)'''
        req = requests.get(self.api_path + ".groups")
        return req.json()
