import webapp2
import init
# from google.appengine.ext import db

Handler= init.Handler

from models.users import Users

class SuccessHandler(Handler):
  """docstring for SuccessHandler
  This class checks if user is logged in.
  If user is logged in the user dashboard is shown
  If user is not logged it redirects to the login page
  """
  def get(self):
    user= self.checkLogin()       # Check if user is logged in
    if user:    # If user is logged in
      # Fetch the username from the cookie value
      username= self.cookieValue("user").split("|")[0]
      data= self.userData(username)     # Fetch all user data by username from datastore   
      
      # If the username and data was fetched successfully
      # Store username and data in a dictionary
      # Render the User Dashboard
      # If the username and data is invalid/could not be fetched
      # Add error messages to header
      # Redirect to Login Page
      if username and data:     
        params= dict(user=username,data=data) 
        self.render('dashboard.html',**params)
      else:
        self.addCookie('retMsg',"Please-login-again!",30)
        self.redirect('/login')
    else:
      self.addCookie('retMsg',"Please-login-again!",30)
      self.redirect('/login')

class LogoutHandler(Handler):
  """docstring for LogoutHandler
  This class helps to logout users
  and empties all user cookie from browser.
  """
  def get(self):
    # Empties the user cookie
    # Checks for referrer url in header
    # Redirect to referrer url if referrer url exists
    # Redirect to mainpage if referrer url does not exist
    if self.checkLogin():
      self.emptyCookie('user')
      ref= self.request.cookies.get('ref')
      self.addCookie('__sucMsg','Come back-again-soon',5)
      if ref:
        self.redirect(ref)
      else:
        self.redirect('/')
    else:
      self.redirect('/login')

app = webapp2.WSGIApplication([
    ('/user/logout', LogoutHandler),
    ('/user/dashboard', SuccessHandler),
    ], 
  debug=True)