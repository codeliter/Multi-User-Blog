import webapp2
import init
import re
from google.appengine.ext import db

Handler= init.Handler

from models.users import Users

class AdminSignupHandler(Handler):
  """docstring for AdminSignUpHandler
  We setup proper authorizations for admin registration.
  Authorization lasts for 5minutes.
  Authorization would be lost if the signup page.
  we are redirected to is refreshed  after 10 seconds.
  """
  def get(self):
    user= self.checkLogin()   # Check if user is logged in
    if not user:              # If user is not logged in
      self.emptyCookie('adminRight')      # Revoke all admin signup authorization    
      cookie= self.genCookie(self.makeSalt(5))    # Generate a secure valid cookie
      self.addCookie('adminRight',cookie,300)     # Add cookie to header
      self.addCookie('adminUrl',"/signup/admin",10)   #add Admin signup Url to header
      #Redirect to signup page with authorization for admin registration 
      self.redirect('/signup') 
    else:                           # If User is logged in
      self.redirect('/user/dashboard')   # Redirect to user dashboard
    
class SignupHandler(Handler):
  """docstring for SignUpHandler
  The signup form is rendered and manipulated by this class.
  All POST request data is validated by this class.
  If all data is valid it is inserted into the database.
  If any/all of the data is invalid necessary errors are thrown and
  signup form is rendered.
  """
  def renderFront(self,**params):
    user= self.checkLogin()
    if not user:
      self.render("signup.html",**params)
    else:
      self.redirect('/user/dashboard')

  def get(self):  
    adminCookie= self.cookieValue('adminRight')      #Fetches Admin Signup cookie value
    # If cookie exists and is valid
    if adminCookie and self.validateCookie(adminCookie) and self.cookieValue('adminUrl') == "/signup/admin":
      params= dict(level=1)     # sets the level to admin
    else:               # If admin cookie does not exist/not valid
      self.emptyCookie('adminRight')
      params= dict(level=2)       # sets the level to user
    self.renderFront(**params)

  def post(self):
    """Stores or post data in respective variables"""
    full_name = self.request.get('full_name')
    name = self.request.get('username')
    pwd = self.request.get('password')
    pwdV = self.request.get('verify')
    email= self.request.get('email')
    level= self.request.get('level')

    
    Err= []     # Initializes the error handler
    error= 0    # Initializes the error counter

    
    if level == 1:      # Checks if signup request is for admin
      adminCookie= self.cookieValue('adminRight')     # Fetch the admin cookie value
      if not self.validateCookie(adminCookie):        # Check cookie validity and throw errors
        Err.append("Admin signup could not be authorised, Please try again")
        error += 1

    if full_name == '':      # If Full name is empty
      Err.append("Please enter your full name")
      error += 1
    elif not re.match(r"^[a-z A-Z]{5,60}$",full_name):   #If you username is valid
      Err.append("Please enter a valid Full name")
      Err.append("A Valid Full name can only accept alphabets and whitespaces")
      Err.append("A Valid Full name must be between 5-60 characters in length")
      error += 1

    if name == '':      # If username is empty
      Err.append("Please enter your username")
      error += 1
    elif not re.match(r"^[a-zA-Z0-9_-]{7,20}$",name):   #If you username is valid
      Err.append("Please enter a valid username")
      Err.append("A Valid username can only accept alphanumerics,dash, and hyphens")
      Err.append("A Valid username must be between 7-20 characters in length")
      error += 1

    if pwd == '' or pwdV == '':     # If password is empty
      Err.append("Please enter a password")
      error += 1
    elif not pwd == pwdV:           # If password matches the verify password field
      Err.append("Passwords do not match")
      error += 1
    elif not re.match(r"^.{6,20}$",pwd):    # If password is valid
      Err.append("Please enter a better password")
      Err.append("A Valid password must be between 6-20 characters in length")
      error += 1

    # If email is valid
    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
      Err.append("Please enter a valid email address")
      error += 1

    # Check if user exist in Datastore
    # Return a single row if user is found
    # If user is not found return none
    checkUser= self.userData(str(name))
    
    if checkUser > 0:         # If user exists throw errors
      Err.append("User already exists")
      error += 1

    # A Dictionary that stores values to be shown if error exists
    params= dict(full_name=full_name,
                  username=name,
                  mail=email,
                  Err=Err
                  )


    # Checks if error exists or not
    # If error exists return form with preserved values
    # If error does not exist add new data to Datastore
    # Generate a valid user cookie
    # Add the User cookie to response headers
    # Redirect to welcome page
    if error > 0:       # If error exist return signup form
      self.renderFront(**params)
    else:               # If error does not exist
      newPass= self.hashPassword(pwd)         #Hash the password
      # Prepare data to be added to datastore
      a= Users(full_name=full_name,
              username=name,
              password=newPass,
              email=email,
              level=int(level))
      a.put()     # Add the Datas above to Datastore

      newUserCookie= str(self.genCookie(name))      # Generate a valid user cookie
      self.addCookie('user', newUserCookie)         # Add cookie to response headers
      self.redirect("/user/dashboard")                   # Redirect to user dashboard                       


app = webapp2.WSGIApplication([
    ('/signup', SignupHandler),
    ('/signup/admin', AdminSignupHandler),
    ], 
  debug=True)