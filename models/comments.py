from google.appengine.ext import db

class Comments(db.Model):
  """docstring for Comments"  
  The Comments Class Creates a valid db kind/model
  for entering post comments data into db
  Attributes: 
        author      (str): The action author
        comment     (str): The comment content
        postid      (int): The post id

  """ 
  comment= db.TextProperty(required = True)
  postid= db.IntegerProperty(required = True)
  author= db.StringProperty(required = True)
  created= db.DateTimeProperty(auto_now_add = True)
