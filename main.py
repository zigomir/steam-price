from google.appengine.api import mail
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template, util
from steam_parse import load_and_return_price
import datetime
import os

STEAM_URL = 'http://store.steampowered.com/app/'
SENDER = 'Steam Price <zigomir@gmail.com>'

class Subscriber(db.Model):
    email = db.StringProperty()
    steam_app_id = db.IntegerProperty()
    price = db.FloatProperty()
    informed = db.BooleanProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    informed_date = db.DateTimeProperty() 

class MainHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, None))
        
class SubscribeHandler(webapp.RequestHandler):
    def post(self):
        email = self.request.get('email')
        price = self.request.get('price')
        steam_app_id = self.request.get('steam_app_id')
        
        subscriber = Subscriber(email=email, 
                                informed=False,
                                informed_date=None,
                                steam_app_id=int(steam_app_id),
                                price=float(price))
        subscriber.put()
        self.send_email(subscriber)
        self.response.out.write('s')
        
    def send_email(self, subscriber):
        mail.send_mail(sender=SENDER,
                  to=subscriber.email,
                  subject="You've subscribed to steam price checker",
                  body="""
        Dear Steam price user:
        
        You've subscribed for a warning when game (%s) will be cheaper than %d EUR.
        
        http://steam-price.appspot.com
        """ % (STEAM_URL + str(subscriber.steam_app_id), subscriber.price))
        
class InformHandler(webapp.RequestHandler):
    def get(self):
        query = Subscriber.all().filter('informed', False)
        
        for subscriber in query:
            price = load_and_return_price(subscriber.steam_app_id)
            if price <= subscriber.price:
                self.send_email(subscriber)
                subscriber.informed = True
                subscriber.informed_date = datetime.datetime.now()
                subscriber.put()
        
    def send_email(self, subscriber):
        # Your application won't work on your Localhost, so upload it
        mail.send_mail(sender=SENDER,
                  to=subscriber.email,
                  subject="Check out new Steam price!",
                  body="""
        Dear Steam price user:
        
        We're pleased to announce, that price of the game (%s) is lower than %d EUR.
        
        http://steam-price.appspot.com
        """ % (STEAM_URL + str(subscriber.steam_app_id), subscriber.price))
       
def main():
    application = webapp.WSGIApplication(
            [('/', MainHandler),
             ('/subscribe', SubscribeHandler),
             ('/inform', InformHandler)
            ],debug=False)
    
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
