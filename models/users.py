from google.appengine.ext import db

class Users(db.Model):
  """docstring for Users
  The Users Class Creates a valid db kind/model
  for entering users data
  
  Attributes:
        full_name   (str): The fullname of the registrant
        username    (str): The username of the registrant
        password    (str): The password of the registrant
        email       (str): The email of the registrant
        level       (int): THe user level 1- admin 2-user
  """

  full_name= db.StringProperty(required=True)
  username= db.StringProperty(required=True)
  password= db.StringProperty(required=True)
  email=    db.StringProperty()
  reg_date=  db.DateTimeProperty(auto_now_add= True)
  level=    db.IntegerProperty(required=True)
