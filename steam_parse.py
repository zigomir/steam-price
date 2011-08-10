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

def find_price(bs):
    priceStr = ''
    try:
        priceStr = bs.find('div', {'class': 'game_area_purchase_game'}) \
                     .find('div', {'class': 'discount_final_price'}).getText().strip()
    except AttributeError:
        # No discount price
        pass
    
    if len(priceStr) == 0:    
        try:
            priceStr = bs.find('div', {'class': 'game_area_purchase_game'}) \
                         .find('div', {'class': 'game_purchase_price price'}).getText().strip()
        except AttributeError:
            # Only discount price'
            pass
    
    priceNum, currency_sign = -1, '$'    
    if len(priceStr) > 0:
        if '&#8364;' in priceStr:
            priceNum, currency_sign = parse_euro(priceStr), '€'
        if '&#36;' in priceStr:
            priceNum, currency_sign = parse_dollar(priceStr), '$'
        if '&#163;' in priceStr:
            priceNum, currency_sign = parse_pound(priceStr), '£'
        if 'Free to Play' in priceStr:
            priceNum = 0
        
    return priceNum, currency_sign

def get_price(steam_app_id, country):
    # load html
    result = urlfetch.fetch(STEAM_URL + str(steam_app_id) + '/?cc=' + country)
    bs = BeautifulSoup(result.content)
    return find_price(bs)
    
def find_title(bs):
    title = ''
    try:
        title = bs.find('div', {'class': 'game_name'}).find('div', {'class': 'blockbg'}).getText().strip()
    except AttributeError:
        pass
    
    return title
    
def get_app_title(steam_app_id, country):
    result = urlfetch.fetch(STEAM_URL + str(steam_app_id) + '/?cc=' + country)
    bs = BeautifulSoup(result.content)
    title = find_title(bs)
    price, currency_sign = find_price(bs)
    return title, price, currency_sign
