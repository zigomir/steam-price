# -*- coding: utf_8 -*-

from google.appengine.api import mail
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template, util
from steam_parse import get_price, get_app_title #@UnresolvedImport
from types import NoneType
import datetime
import os

STEAM_URL = 'http://store.steampowered.com/app/'
SENDER = 'Steam Price <zigomir@gmail.com>'


class Subscriber(db.Model):
    email = db.StringProperty()
    steam_app_id = db.IntegerProperty()
    price = db.FloatProperty()
    country = db.StringProperty()
    steam_app_title = db.StringProperty()
    price_with_currency = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    
    informed = db.BooleanProperty()
    informed_date = db.DateTimeProperty() 

class MainHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        country = self.request.headers.get('X-AppEngine-country')
        if isinstance(country, NoneType):   # for localhost testing only, because this header is only on production server
            country = 'si'
        if len(country) == 0:
            country = 'si'
            
        template_values = {'country': country.lower()}
        self.response.out.write(template.render(path, template_values))
        
class SubscribeHandler(webapp.RequestHandler):
    def post(self):
        email = self.request.get('email')
        price = self.request.get('price')
        steam_app_id = self.request.get('steam_app_id')
        country = self.request.get('country')
        steam_app_title = self.request.get('steam_app_title_input')
        price_with_currency = self.request.get('price_with_currency')
        
        subscriber = Subscriber(email=email, 
                                steam_app_id=int(steam_app_id),
                                country=country,
                                price=float(price),
                                steam_app_title=steam_app_title,
                                price_with_currency=price_with_currency,
                                informed=False,
                                informed_date=None)
        subscriber.put()
        self.send_email(subscriber)
        self.response.out.write('s')
        
    def send_email(self, subscriber):
        mail.send_mail(sender=SENDER,
                  to=subscriber.email,
                  subject="You have subscribed to Steam price notifier",
                  body="""
        You've subscribed for a notify when %s (%s) will cost less than %s
        
        http://steam-price.appspot.com
        """ % (subscriber.steam_app_title, STEAM_URL + str(subscriber.steam_app_id), subscriber.price_with_currency)
        )
        
class InformHandler(webapp.RequestHandler):
    def get(self):
        query = Subscriber.all().filter('informed', False)
        
        for subscriber in query:
            price, _ = get_price(subscriber.steam_app_id, subscriber.country)
            
            if price <= subscriber.price:
                self.send_email(subscriber)
                subscriber.informed = True
                subscriber.informed_date = datetime.datetime.now()
                subscriber.put()
        
    def send_email(self, subscriber):
        # Your application won't work on your Localhost, so upload it
        mail.send_mail(sender=SENDER,
                  to=subscriber.email,
                  subject="%s has new price!" % subscriber.steam_app_title,
                  body="""
        Price of the game %s (%s) is lower than %s.
        
        http://steam-price.appspot.com
        """ % (subscriber.steam_app_title, STEAM_URL + str(subscriber.steam_app_id), subscriber.price_with_currency)
        )

    
class AppTitleHandler(webapp.RequestHandler):
    def get(self, steam_app_id):
        country = self.request.headers.get('X-AppEngine-country')
        if isinstance(country, NoneType):   # for localhost testing only, because this header is only on production server
            country = 'si'
        
        title, price, currency_sign = get_app_title(steam_app_id, country)
        price_with_currency = self.get_price_in_currency(price, currency_sign)
        if title == '':
            title = 'null'
        # without str for title I would get strange ascii error. don't know if it's appengine bug
        json_response = '{"title": "%s", "price": %.2f, "currency_sign": "%s", "price_with_currency": "%s"}' %  \
                        (str(title), price, currency_sign, price_with_currency)
        self.response.out.write(json_response)
        
    def get_price_in_currency(self, price, currency_sign):
        if price == 0:
            return "Free to Play"
        
        if currency_sign == '€':
            return ("%.2f" % price).replace('.', ',') + currency_sign
        else:
            return currency_sign + ("%.2f" % price)
       
def main():
    application = webapp.WSGIApplication(
            [('/', MainHandler),
             ('/subscribe', SubscribeHandler),
             ('/inform', InformHandler),
             ('/app_title/([^/]+)?', AppTitleHandler)
            ],debug=False)
    
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
