import webapp2
import init
from google.appengine.ext import db
import codecs
import re
import string

Handler= init.Handler

from models.posts import Post
from models.posts import PostAction
from models.comments import Comments
from models.users import Users

class updatePostHandler(Handler):
  """docstring for updatePostHandler
    This class helps in modifying a blog post
    It checks if user has the proper rights to update a post
  """
  def renderFront(self, **params):
    checkLogin= self.checkLogin()       # Checks to see if user is logged in
    if checkLogin:                      # If user is logged in
      self.render('editpost.html',**params)  # Allow Post modification
    else:
      self.addCookie("__retMsg","Please-login-first",5)
      self.redirect("/login")    # Redirect to login page

  def get(self,postId):
    # Check if Post exists
    checkPosts= Post.get_by_id(int(postId))
    if checkPosts:      # If post exists
      username= self.cookieValue("user").split("|")[0]    # Fetch userName

      if username == checkPosts.creator:
        params= dict(title=checkPosts.subject,
                    content=checkPosts.content,
                    )
        self.renderFront(**params)
      else:
        self.addCookie("__retMsg","You do not have permissions to modify this post",5)
        self.redirect("/post/%s" % postId)
    else:             # If post does not exist
      self.addCookie("__retMsg","Post-does-not-exist",5)
      self.redirect("/")

  def post(self,postId):
    checkLogin= self.checkLogin()       # Checks to see if user is logged in

    if checkLogin:                      # If user is logged in  
      subject = self.request.get("title")         # The post title
      content = self.request.get("content")       # The post content

      error = []              # Initialize error container
      if not subject:         # If post title is not set
        error.append("Please enter post title")

      if not content:         # If content is not sent
        error.append("Please enter post content")

      # Store values and errors in a dictionary
      params= dict(error= error,
                      title= subject,
                      content= content,
                      )

      # If no error was thrown
      # Prepare data to be updated into the Datastore
      # Update Data to the Datastore
      # Redirect to the Just Updated Post
      # If error was thrown
      # Show the form again and display errots
      update= Post.get_by_id(int(postId))
      username= self.cookieValue("user").split("|")[0]

      if not username == update.creator:
        self.addCookie("__retMsg","You do not have permissions to modify this post",5)
        self.redirect("/post/%s" % postId)

      if not error:
        # Prepare the data to be update
        update.subject= subject       
        update.content= content
        if update.put():
          self.addCookie('__sucMsg',"Post Updated successfully",5)
        else:
          self.addCookie('__retMsg',"Please try again!")
        self.redirect('/post/'+str(update.key().id()))
      else:
        self.renderFront(**params)
    else:                 # If user is not logged in
      self.addCookie("__retMsg","Please-login-first",5)
      self.redirect("/login")    # Redirect to login page

class BlogPostHandler(Handler):
  """BlogPost class shows the blog posts"""
  def getActions(self, action, postId):         #Funtion to get Action
    q= db.GqlQuery('''SELECT * FROM PostAction 
                          WHERE action=:1 AND postid=:2''',
                          int(action),int(postId))
    count= 0
    for i in q:
      count += 1
    return count

  def renderFront(self, **params):
    params['content']= params['content'].replace('\n',"<br>")
    self.render('viewpost.html',**params)

  def get(self,blog_id):
    if not blog_id:         # If blogID is not set
      self.error('404')     # Return 404
    else:               # If blogID is set
      s = Post.get_by_id(int(blog_id))      # Fetch blog post data by ID
      if not s:       # IF blog post does not exist
        self.addCookie("__retMsg","Post-does-not-exist",5)
        self.redirect('/')    #Redirect to Homepage
      else:
        Likes= self.getActions(1,blog_id)   # Store in a list
        DisLikes= self.getActions(2,blog_id)    #store in a list
        comments= db.GqlQuery('''SELECT * FROM Comments 
                              WHERE postid=:1
                              ORDER BY created DESC
                              LIMIT 0,10''',
                              int(blog_id))
        
        params= dict(comments= comments,
                    likes= Likes,
                    dislikes= DisLikes,
                    date=s.created,
                    title=s.subject,
                    content=s.content,
                    creator=s.creator,
                    postId=blog_id,
                    last_modified= s.last_modified
                    )
        self.renderFront(**params)

  def post(self,postId):
    checkPosts= Post.get_by_id(int(postId))    # Fetch post data
    if checkPosts:            # If post exists
      checkLogin= self.checkLogin()       # Checks to see if user is logged in
      if checkLogin:                      # If user is logged in  
        username= self.cookieValue("user").split("|")[0]   # Fetch username for cookie 
        data= self.userData(username)     # fetch user data
        if data:      # If user data was fetched successfully
          username= data.username
          comment= self.request.get('content')
          if not comment:
            self.addCookie("__retMsg","Please-enter-a-comment!",5)
            self.redirect("/post/%s" % postId)
          #Prepare data to be stored to database
          a=  Comments(comment=comment, author=username, postid=int(postId)) 
          if a.put():
            self.addCookie("__sucMsg","Thanks-for-sharing-your-thoughts!",5)
            self.redirect("/post/%s" % postId)
          else:
            self.addCookie("__retMsg","Please-try-again!",5)
            self.redirect("/post/%s" % postId)
        else:         # If user data could not be fetched
          self.addCookie("__retMsg","Please-try-again!",5)
          self.redirect("/post/%s" % postId)
      else:     # If user is not logged in
        self.addCookie("__retMsg","Please-login-first",5)
        self.redirect("/login")
    else:
      self.addCookie("__retMsg","Post-does-not-exist",5)
      self.redirect("/")


class newPostHandler(Handler):
  """docstring for newPostHandler
    This class helps in creating a blog post
    It checks if user has the proper rights to add a post
  """
  def renderFront(self, **params):
    checkLogin= self.checkLogin()       # Checks to see if user is logged in
    if checkLogin:                      # If user is logged in
      username= self.cookieValue("user").split("|")[0]   # Fetch username for cookie 
      data= self.userData(username)     # fetch user data

      if data.level == 1:               # If user is an admin(User level == 1)
        self.render('newpost.html',**params)  # Allow Post creation
      else:   # If user is not admin
        self.addCookie("__retMsg","You-are-not-permitted-to-add-post",5)
        self.redirect("/")    # Redirect to Blog Posts
    else:
      self.addCookie("__retMsg","Please-login-first",5)
      self.redirect("/login")    # Redirect to login Page

  def get(self):
    self.renderFront()

  def post(self):
    checkLogin= self.checkLogin()       # Checks to see if user is logged in
    if checkLogin:                      # If user is logged in  
      username= self.cookieValue("user").split("|")[0]   # Fetch username for cookie 
      data= self.userData(username)     # fetch user data
      if data.level == 1:               # If user is an admin(User level == 1)
        subject = self.request.get("title")         # The post title
        content = self.request.get("content")       # The post content
        creator = data.username                     # The post username

        error = []              # Initialize error container
        if not subject:         # If post title is not set
          error.append("Please enter post title")

        if not content:         # If content is not sent
          error.append("Please enter post content")

        # Store values and errors in a dictionary
        params= dict(error= error,
                      title= subject,
                      content= content)

        # If no error was thrown
        # Prepare data to be entered into the Datastore
        # Add Data to the Datastore
        # Redirect to the Just Created Post
        # If error was thrown
        # Show the form again and displaya erroes
        if not error:
          self.addCookie("__sucMsg","Post-created-successfully",5)
          a= Post(subject= subject,content = content,creator = creator)
          a.put()
          self.redirect('/post/'+str(a.key().id()))
        else:
          self.renderFront(**params)
      else:   #If user is not an admin
        self.addCookie("__retMsg","You-are-not-permitted-to-add-post",5)
        self.redirect("/")    # Redirect to Blog Posts
    else:                 # If user is not logged in
      self.addCookie("__retMsg","Please-login-first",5)
      self.redirect("/login")    # Redirect to Blog Posts


class postActionHandler(Handler):
  """docstring for postActionHandler
  This handles different action requests such as like, delete unlike
  """
  def get(self,action,postId):
    # Check if Post exists
    checkPosts= Post.get_by_id(int(postId))
    if checkPosts:      # If post exists
      checkLogin= self.checkLogin()       # Checks to see if user is logged in
      if checkLogin:                      # If user is logged in  
        username= self.cookieValue("user").split("|")[0]   # Fetch username for cookie 
        data= self.userData(username)     # fetch user data
        if data:      # if user data was fetched successfully
          username= data.username         # Store the username of the logged in user
          creator= checkPosts.creator     # Store the post creator
          if action == 'like':            # If requested action is a like
            if not username == creator: # If user is not the creator of the post
              # Check if user already likes the post
              getLikes= db.GqlQuery('''SELECT * FROM PostAction 
                                    WHERE action=:1 AND author=:2 
                                    AND postid=:3''',
                                    1,str(username),int(postId)).get()
              if not getLikes:      #if user does not like the post add likes to entry
                # Check if user already dislikes the post
                getDisLikes= db.GqlQuery('''SELECT * FROM PostAction 
                                    WHERE action=:1 AND author=:2 
                                    AND postid=:3''',
                                    2,str(username),int(postId)).get()
                if getDisLikes:       # Update the entry if user already likes this post
                  a= getDisLikes
                  a.action= 1
                else:           # Create entry if user does not already like this post
                  a=  PostAction(action=1, author=username, postid=int(postId))
                if a.put():
                  self.addCookie('sucMsg','Thanks for the love',5)
                else:
                  self.addCookie('sucMsg','Please try again!',5)
                self.redirect("/post/%s" % postId)
              else:       # IF user already likes this post
                self.addCookie("__retMsg","You-already-like-this-post",5)
                self.redirect("/post/%s" % postId)
            else:         # If post creator is trying to like own post
              self.addCookie("__retMsg","You-cannot-like-this-post",5)
              self.redirect("/post/%s" % postId)
          
          elif action == 'dislike':           # If requested action is a dislike
            if not username == creator: # If user is not the creator of the post
              # Check if user already dislikes the post
              getDisLikes= db.GqlQuery('''SELECT * FROM PostAction 
                                    WHERE action=:1 AND author=:2 
                                    AND postid=:3''',
                                    2,str(username),int(postId)).get()
              if not getDisLikes:      #if user does not dislike the post add/update likes to entry
                #Check if user already Likes this post
                Like= db.GqlQuery('''SELECT * FROM PostAction 
                                    WHERE action=:1 AND author=:2 
                                    AND postid=:3''',
                                    1,str(username),int(postId)).get()
                if Like:       # Update the entry if user already dislikes this post
                  a= Like
                  a.action= 2
                else:           # Create entry if user does not already dislike this post
                  a=  PostAction(action=2, author=username, postid=int(postId))
                if a.put():
                  self.addCookie('retMsg','We hope to get better! Sorry for any incovenience',5)
                else:
                  self.addCookie('sucMsg','Please try again!',5)
                self.redirect("/post/%s" % postId)
              else:   # IF user already dislikes this post
                self.addCookie("__retMsg","You-already-dislike-this-post",5)
                self.redirect("/post/%s" % postId)
            else:     # If post creator is trying to dislike own post
              self.addCookie("__retMsg","You-cannot-dislike-this-post",5)
              self.redirect("/post/%s" % postId)
          elif action == 'delete':                #If Post is to be deleted
            if username == creator:  
              checkPosts.delete()    
              if checkPosts:               # If Post could be deleted
                self.addCookie("__sucMsg","Post-was-deleted-successfully",5)
                self.redirect("/")          # Redirect to homepage
              else:
                self.addCookie("__retMsg","Post-was-not-deleted-Try-again!",5)
                self.redirect("post/%s" % postId)          # Redirect to the post
            else:
              self.addCookie("__sucMsg","You do not have permissions to delete this post",5)
              self.redirect("post/%s" % postId)          # Redirect to homepage

        else:         # If user data could not be fetched
          self.redirect("/post/%s" % postId)
      else:     # If user is not logged in
        self.addCookie("__retMsg","Please-login-first",5)
        self.redirect("/login")
    else:     # If post does not exist
      self.addCookie("__retMsg","Post-does-not-exist",5)
      self.redirect("/")


app = webapp2.WSGIApplication([
    ('/post/add', newPostHandler),
    ('/post/([0-9]+)', BlogPostHandler),
    ('/post/edit/([0-9]+)', updatePostHandler),
    ('/post/([a-z]+)/([0-9]+)',postActionHandler),
    ], 
	debug=True)