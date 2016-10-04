import webapp2
import init
from google.appengine.ext import db

Handler= init.Handler

from models.comments import Comments
from models.posts import Post
from models.users import Users

class deleteCommentHandler(Handler):
  """docstring for deleteCommentHandler
    This class helps in deleting a user comment
    It checks if user has the proper rights to delete a comment
  """
  def get(self,commentId):
    checkLogin= self.checkLogin()       # Checks to see if user is logged in
    if checkLogin:                      # If user is logged in
      comment= Comments.get_by_id(int(commentId))
      if comment:
        postid= comment.postid
        username= self.cookieValue("user").split("|")[0]
        if username == comment.author:       # If the requester is the the comment author
          comment.delete()
          if comment:               # If comment was deleted
            self.addCookie("__sucMsg","Comment was deleted successfully",5)
            self.redirect("/post/%s" % postid)      # Redirect to homepage
          else:
            self.addCookie("__retMsg","Please Try-again!",5)
            self.redirect("/post/%s" % postid)          # Redirect to the post
        else:
          self.addCookie("__sucMsg","You do not have permissions to delete this comment",5)
          self.redirect("/post/%s" % postid)          # Redirect to homepage
      else:
          self.addCookie("__retMsg","Comment does not exist",5)
          self.redirect("/")          # Redirect to homepage
    else:
      self.addCookie("__retMsg","Please login first",5)
      self.redirect("/")          # Redirect to homepage
  
class updateCommentHandler(Handler):
  """docstring for updateCommentHandler
    This class helps in modifying a user comment
    It checks if user has the proper rights to update a comment
  """
  def renderFront(self, **params):
    checkLogin= self.checkLogin()       # Checks to see if user is logged in
    if checkLogin:                      # If user is logged in
      self.render('editcomment.html',**params)  # Allow comment modification
    else:
      self.addCookie("__retMsg","Please-login-first",5)
      self.redirect("/login")    # Redirect to login page

  def get(self,commentId):
    # Check if comment exists
    checkCom= Comments.get_by_id(int(commentId))
    if checkCom:      # If post exists
      username= self.cookieValue("user").split("|")[0]    # Fetch userName

      if username == checkCom.author:
        params= dict(
                    content=checkCom.comment,
                    )
        self.renderFront(**params)
      else:
        self.addCookie("__retMsg","You do not have permissions to modify this comment",5)
        self.redirect("/post/%s" % checkCom.postid)
    else:             # If post does not exist
      self.addCookie("__retMsg","Comment-does-not-exist",5)
      self.redirect("/")

  def post(self,commentId):
    checkLogin= self.checkLogin()       # Checks to see if user is logged in

    if checkLogin:                      # If user is logged in  
      content = self.request.get("content")       # The comment

      error = []              # Initialize error container

      if not content:         # If content is not sent
        error.append("Please enter post content")

      # Store values and errors in a dictionary
      params= dict(error= error,
                      content= content,
                      )

      # If no error was thrown
      # Prepare data to be updated into the Datastore
      # Update Data to the Datastore
      # Redirect to the Parent Post
      # If error was thrown
      # Show the form again and display errors
      update= Comments.get_by_id(int(commentId))
      username= self.cookieValue("user").split("|")[0]

      if not username == update.author:
        self.addCookie("__retMsg","You do not have permissions to modify this comment",5)
        self.redirect("/post/%s" % update.postid)

      if not error:
        update.comment= content
        if update.put():
          self.addCookie('__sucMsg',"Comment Updated successfully",5)
        else:
          self.addCookie('__retMsg',"Please try again!")
        self.redirect('/post/'+str(update.postid))
      else:
        self.renderFront(**params)
    else:                 # If user is not logged in
      self.addCookie("__retMsg","Please-login-first",5)
      self.redirect("/login")    # Redirect to Blog Posts

app = webapp2.WSGIApplication([
    ('/comment/edit/([0-9]+)', updateCommentHandler),
    ('/comment/delete/([0-9]+)', deleteCommentHandler),
    ], 
  debug=True)