import webapp2
import init
from google.appengine.ext import db

Handler= init.Handler

from models.users import Users

class LoginHandler(Handler):
  """docstring for LoginHandler
  This Class Shows the Login Interface
  Signs in and Authorizes a valid user
  Redirects to the User Dashboard
  """
  def renderFront(self,**params):
    user= self.checkLogin()   # Checks if user is already logged in
    if not user:              # If user is not Logged in
      self.render("login.html",**params)  #Showthe Login Form
    else:                     # If user is Logged in
      self.redirect('/user/dashboard')   # Redirect to the user dashboard

  def get(self):
    self.renderFront()

  def post(self):
    name = self.request.get('username')         #Username variable
    pwd = self.request.get('password')          #Password variable

    Err= []         # Initialize the error container

    if name == '':      # If Username is empty
      Err.append("Please enter your username")

    if pwd == '':       # If Password is empty
      Err.append("Please enter a password")

    q= self.userData(str(name))     # Check If user exists
    if not q:                       # If user does not exist
      Err.append('User account does not exist!')

    if not Err and q:             # If their were no errors and user exists
      password= str(q.password)   # Fetch user password
      
      # Verify if password inputed matches the password in user account
      checkLogin= self.verifyHash(pwd,password)
      if checkLogin:        # If password match
        newCookie= str(self.genCookie(name))    # Generate a valid user cookie
        self.addCookie('user',newCookie)        # Add user cookie to head
        self.redirect('/user/dashboard')             # Redirect to user dashboard
      else:     # If passwords do not matcg
        Err.append('Username/Password is incorrect')  # Add error to error container
        # Preserve inputed data and errors in a dictionary
        # Shows the Login form again
        params= dict(Err = Err,
                    username= name)
        self.render("login.html",**params)
    else:       # If their were errors or user does not exists
      # Preserve inputed data and errors in a dictionary
      # Shows the Login form again
      params= dict(Err = Err,
                    username= name)
      self.render("login.html",**params)

app = webapp2.WSGIApplication([
    ('/login', LoginHandler),
    ], 
  debug=True)