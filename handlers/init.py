import os
import webapp2

import codecs
import jinja2
import re
import string
import hashlib
import random
import hmac
import datetime

from google.appengine.ext import db
from models.users import Users

templateDir= os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
staticDir= os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
jinja_env= jinja2.Environment(loader = jinja2.FileSystemLoader(templateDir),
                              autoescape= True
                              )

secret= 'f2175c91b5f63dace8a242d53222c0'

class Handler(webapp2.RequestHandler):
  """This Handler class creates a new instance 
    of the Google App engine Request Handler 
  """
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def renderStr(self, template, **params):
    t= jinja_env.get_template(template)
    return t.render(params)

  def render(self, template, **kw):
    # Global Variable to acccess all error messages stored in cookie
    jinja_env.globals['__retMsg']= self.cookieValue('__retMsg')   
    # Global Variable to acccess all success messages stored in cookie
    jinja_env.globals['__sucMsg']= self.cookieValue('__sucMsg')   
     # Global Variable to establish login state
    jinja_env.globals['__LoggedIn']= self.checkLogin()
    if self.checkLogin():   # If user is Logged in
      # Fetch user data and make it available site-wide
      userName= self.cookieValue('user').split('|')[0]
      jinja_env.globals['__myUserData']= self.userData(userName)
    self.write(self.renderStr(template, **kw))

  # Adds a cookie to headers
  def addCookie(self,cookieName, cookieValue, expiryTime=''):
    cookieValue= cookieValue.replace(' ','-')
    if expiryTime:
      exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=expiryTime) # expiry time in seconds
      expires = exp.strftime("%a, %d %b %Y %H:%M:%S GMT")
      self.response.headers.add_header('Set-Cookie','%s=%s; Expires=%s; Path=/;' 
                                        % (cookieName,cookieValue,expires))
    else:
       self.response.headers.add_header('Set-Cookie','%s=%s; Path=/;' 
                                        % (cookieName,cookieValue))

  # Deletes a cookie value from headers
  def emptyCookie(self,cookieName):
    self.response.headers.add_header('Set-Cookie','%s=; Path=/; Expires=Thu, 01-Jan-1970 00:00:10 GMT;' % cookieName)
  
  # Hashes a cookie
  def hashCookie(self, value):
    return hmac.new(secret,value).hexdigest()

  # Generates a valid cookie
  def genCookie(self, value):
    hash= self.hashCookie(value)
    return value+"|"+hash

  # Validates a cookie
  def validateCookie(self, cookie):
    s= cookie.split("|")

    return len(s) > 1 and s[1] == self.hashCookie(s[0])

  # returns cookie value 
  def cookieValue(self, name):
    value= self.request.cookies.get(name)
    if value:
      return value

  # Creates a valid random salt fo hashing password
  def makeSalt(self, limit=7):
    return ''.join(random.choice(string.letters) for i in range(limit))

  # Hashes a pasword using a randomly generated salt
  def hashPassword(self,password,salt=''):
    if not salt:
      salt = self.makeSalt()

    return hashlib.sha256(password + salt).hexdigest()+','+salt
  
  # Verifies a Hashed password for validity
  def verifyHash(self,password,hashed):
    salt= hashed.split(',')[1]
    passHash= self.hashPassword(password,salt)
    if passHash == hashed:
      return True
  # Returns user data by username
  def userData(self,username):
    data= db.GqlQuery("SELECT * FROM Users WHERE username=:1",str(username)).get()
    return data

  def checkLogin(self):
    nameCookie= self.request.cookies.get('user')

    if nameCookie:
      username= self.cookieValue('user').split('|')[0]
      data= self.userData(username)
      if data:
        return True
    else: 
      self.emptyCookie("user")
      return False

