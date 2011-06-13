from BeautifulSoup import BeautifulSoup
from google.appengine.api import urlfetch

STEAM_URL = 'http://store.steampowered.com/app/'

def parse_euro(str):
    i = str.find(',')
    numText = str[:i + 3].replace(',', '.')
    return float(numText)
    
def parse_dollar(str):
    numText = str[1:len(str)]
    return float(numText)

def load_and_return_price(steam_app_id):
    # load html
    result = urlfetch.fetch(STEAM_URL + str(steam_app_id))
    bs = BeautifulSoup(result.content)
    
    # find vs findAll
    priceStr = ''
    try:
        priceStr = bs.find('div', {'class': 'discount_final_price'}).getText().strip()
    except AttributeError:
        # No discount price
        pass
    
    if len(priceStr) == 0:    
        try:
            priceStr = bs.find('div', {'class': 'game_purchase_price price'}).getText().strip()
        except AttributeError:
            # Only discount price'
            pass
    
    if len(priceStr) > 0:
        if '&#8364;' in priceStr:
            priceNum = parse_euro(priceStr)
        if '&#36;' in priceStr:
            priceNum = parse_dollar(priceStr)
        return priceNum