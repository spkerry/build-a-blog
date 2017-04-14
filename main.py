import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def get(self):
        self.render("main-page.html")

class NewPost(Handler):
    def get(self, title="", body="", error=""):
        self.render("new-post.html", title=title, body=body, error=error)

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if body and title:
            b = Blog(title = title, body = body)
            b.put()
            b.key().id()
            self.render("single-post.html", title=title, body=body)
        else:
            error = "we need both a title and your blog!"
            self.render("new-post.html", title=title, body=body, error=error)

class BlogPage(Handler):
    def get(self, title="", body=""):
        blogs = db.GqlQuery("SELECT * FROM Blog "
                           "ORDER BY created DESC "
                           "LIMIT 5 ")

        self.render("blog.html", title=title, body=body, blogs=blogs)

class ViewPostHandler(Handler):
    def get(self, id):
        valid_post = Blog.get_by_id(int(id))

        if not valid_post:
            error_title = "nothing here!"
            error_body = "there is no post with id " + id
            self.render("single-post.html", title = error_title, body = error_body)
        else:
            self.render("single-post.html", title = valid_post.title, body = valid_post.body)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', BlogPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
