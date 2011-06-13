# -*- coding: utf_8 -*-

from BeautifulSoup import BeautifulSoup
from google.appengine.api import urlfetch

STEAM_URL = 'http://store.steampowered.com/app/'

def parse_euro(str):
    i = str.find(',')
    numText = str[:i + 3].replace(',', '.')
    return float(numText)
    
def parse_dollar(str):
    str = str.replace('USD', '').strip()    # country code wf for example
    numText = str[5:len(str)]
    return float(numText)

def parse_pound(str):
    numText = str[6:len(str)]
    return float(numText)

def load_and_return_price(steam_app_id, country):
    # load html
    result = urlfetch.fetch(STEAM_URL + str(steam_app_id) + '/?cc=' + country)
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
            priceNum, currency_sign = parse_euro(priceStr), '€'
        if '&#36;' in priceStr:
            priceNum, currency_sign = parse_dollar(priceStr), '$'
        if '&#163;' in priceStr:
            priceNum, currency_sign = parse_pound(priceStr), '£'
            
        return priceNum, currency_sign