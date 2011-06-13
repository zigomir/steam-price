from google.appengine.api import urlfetch


STEAM_URL = 'http://store.steampowered.com/app/'

def get_price_for_id(app_id):
    result = urlfetch.fetch(STEAM_URL + app_id)
    return result.content
