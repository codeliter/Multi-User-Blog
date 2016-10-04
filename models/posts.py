from google.appengine.ext import db
class Post(db.Model):
  """docstring for Post 
  The Post Class Creates a valid db kind/model
  for entering post data
  Attributes: 
        subject   (str): The title of the post
        content   (str): The content of the post
        creator   (str): The post author

  """ 
  subject= db.StringProperty(required = True)
  content= db.TextProperty(required = True)
  creator= db.TextProperty(required = True)
  created= db.DateTimeProperty(auto_now_add = True)
  last_modified= db.DateTimeProperty(auto_now= True)


class PostAction(db.Model):
  """docstring for PostAction
  The PostAction Class Creates a valid db kind/model
  for entering post actions data
  Attributes: 
        action   (str): The type of action (like/dislike/delete)
        author   (str): The action author
        postid   (int): The post id

  """ 
  action= db.IntegerProperty(required = True)
  postid= db.IntegerProperty(required = True)
  author= db.StringProperty(required = True)
  created= db.DateTimeProperty(auto_now_add = True)