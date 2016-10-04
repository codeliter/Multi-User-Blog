import webapp2
import init
from google.appengine.ext import db

Handler= init.Handler

from models.posts import Post
from models.users import Users

class MainPage(Handler):
  """docstring for Mainpage
  The MainPage class renders the main page/landing page"""
  def renderFront(self, **params):
    posts= db.GqlQuery('SELECT * FROM Post ORDER BY created DESC LIMIT 0,11')
    if posts:
      params['posts']= posts
    
    self.render('index.html',**params)

  def get(self):
    self.renderFront()





 
app = webapp2.WSGIApplication([
    ('/', MainPage),
    # ('/signup', SignupHandler),
    # ('/signup/admin', AdminSignupHandler),
    # ('/login', LoginHandler),
    # ('/logout', LogoutHandler),
    # ('/dashboard', SuccessHandler),
    # ('/post/add', newPostHandler),
    # ('/post/([0-9]+)', BlogPostHandler),
    # ('/post/edit/([0-9]+)', updatePostHandler),

    # ('/post/([a-z]+)/([0-9]+)',postActionHandler),
    ], 
	debug=True)