#imports
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


#app setup and config settings
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'y337kGcys&P3B'
db = SQLAlchemy(app)

#Blog class is setup to hold the main database of the blog storing things such as each
#blog title, the content of that blog and in the future likes/dislikes/comments
class Blog(db.Model):
    #current required info when creating a blog post is the blog title and text content
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(40000))
    
    #initilizes the blog post
    def __init__(self, title, body):
        self.title = title
        self.body = body

#if someone accesses the root of the website they're redirected to the blog route
@app.route('/', methods=['POST','GET'])
def index():
    #simple redirect incase no path was given
    return redirect('/blog')
        
#renders the main blog page, pulling all items from the blog db and rendering them dynamically 
#todo- add sorting function
@app.route('/blog', methods=['POST','GET'])
def blog():
    blog_post = Blog.query.all()
    newest_post_first = Blog.query.order_by(Blog.id.desc()).all()
    print(newest_post_first)
    #this line could be better it handles pulling an id if the user has given me one
    if request.method == 'GET':
        blog_id = request.args.get('id')
        #this checks if there is even a blog id argument and then renders a page for the post clicked by the user
        if blog_id:
            requested_post = Blog.query.get(blog_id)
             
            return render_template('post.html',title="Post",blog_title=requested_post.title,body=requested_post.body)
    
    #this is how the page renders if no arguments are given in the url
    return render_template('blog.html',title="Blog",blog=newest_post_first)

#renders the new post page where anybody can create a new post for the blog
@app.route('/newpost', methods=['POST','GET'])
def newpost():
    #error message variable creation
    title_error = ""
    content_error = ""
    #blog post variables
    blog_title = ""
    blog_content = ""
    
    #load the page for the user with no error messages
    if request.method == 'GET':
        return render_template('newpost.html',title="Create Post", title_error=title_error,content_error=content_error
                           ,blog_post_title=blog_title,blog_post_content=blog_content)
    
    #when the user hits the post button on the page their information is taken and
    #submitted into the database if criteria met
    if request.method == 'POST':
        blog_title = request.form['blog_post_title']
        blog_content = request.form['blog_post_content']
        new_blog_post = Blog(blog_title, blog_content) 
    
    #validation to make sure a blog title and body are given
    #error message given if forgotten
        if not blog_title:
            title_error = "Required"
        if not blog_content:
            content_error = "Required"
        
    #if no errors found then add the data to db and redirect user to new blog post page 
    if not title_error and not content_error:
        db.session.add(new_blog_post)
        db.session.commit()
        post_id = new_blog_post.id
        #above grabs the id of the post that was just put into the db
        #then below it redirects you to the new blog page of your post based on the id 
        #that was grabbed
        return redirect('/blog?id={0}'.format(str(post_id)))
    
    #render the page with helpful error messages           
    return render_template('newpost.html',title="Create Post", title_error=title_error,content_error=content_error
                           ,blog_post_title=blog_title,blog_post_content=blog_content)

#standard
if __name__ == '__main__':
    app.run()