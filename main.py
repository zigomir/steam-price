from google.appengine.api import mail
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template, util
from steam_communication import get_price_for_id
import os

class Subscriber(db.Model):
    email = db.StringProperty()
    steam_app_id = db.IntegerProperty()
    price = db.FloatProperty()
    informed = db.BooleanProperty()
    date = db.DateTimeProperty(auto_now_add=True)

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
                                steam_app_id=int(steam_app_id),
                                price=float(price))
        subscriber.put()
        self.response.out.write('s')
        
class CheckHandler(webapp.RequestHandler):
    def get(self):
        query = Subscriber.all().filter('informed', False)
        
        subscribers = []
        for subscriber in query:
            subscribers.append(subscriber)
            
        values = {'subscribers' : subscribers}
            
        path = os.path.join(os.path.dirname(__file__), 'templates/check.html')
        self.response.out.write(template.render(path, values))
        
    def post(self):
        steam_app_id = self.request.get('steam_app_id')
        self.response.out.write(get_price_for_id(steam_app_id))
        
class InformHandler(webapp.RequestHandler):
    def post(self):
        id_to_inform = self.request.get('id_to_inform')
        subscriber = Subscriber.get_by_id(int(id_to_inform))
        
        STEAM_URL = 'http://store.steampowered.com/app/'
        
        # Your application won't work on your Localhost, so upload it
        mail.send_mail(sender="Steam Price <zigomir@gmail.com>",
                  to=subscriber.email,
                  subject="Check out new Steam price!",
                  body="""
        Dear Steam price User:
        
        We're pleased to announce, that price of the game (%s) is lower than %d EUR.
        
        http://steam-price.appspot.com
        """ % (STEAM_URL + str(subscriber.steam_app_id), subscriber.price))
        
        subscriber.informed = True
        subscriber.put()
       
def main():
    application = webapp.WSGIApplication(
            [('/', MainHandler),
             ('/subscribe', SubscribeHandler),
             ('/check', CheckHandler),
             ('/inform', InformHandler)
            ],debug=False)
    
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
