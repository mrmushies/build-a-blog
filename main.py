import webapp2
import cgi
import jinja2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Home(Handler):
    def get(self):
        self.render("home.html")

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Blog(db.Model):
    subject = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)


class BlogPage(Handler):
    def render_home(self, subject="", body="", error=""):
        bposts = db.GqlQuery("SELECT * from Blog "
                           "ORDER BY created DESC "
                           " LIMIT 5 ")

        self.render("blog.html", subject = subject, body = body, error = error, bposts = bposts)


    def get(self):
        self.render_home()



class NewPost(Handler):
    def render_newpost(self, subject="", body="", error=""):


        self.render("NewPost.html", subject = subject, body = body, error = error)


    def get(self):
        self.render_newpost()


    def post(self):
        subject = self.request.get("subject")
        body = self.request.get("body")
        if subject and body:
            b = Blog(subject = subject, body = body)
            b.put()

            self.redirect("/blog")
        else:
            error = "We need both a title and art"
            self.render_newpost(subject, body, error)

class ViewPostHandler(Handler):
    def get(self, idn):

        post = Blog.get_by_id(int(idn))

        self.render("blog.html", bposts = [post])

        if not post:
            self.error(404)
            return


app = webapp2.WSGIApplication([
    ('/', Home),
    ('/blog', BlogPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<idn:\d+>', ViewPostHandler)
], debug=True)
