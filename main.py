#imports
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


#app setup and config settings
app = Flask(__name__)
app.config['DEBUG'] = True
#links app to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Blogz:password@localhost:8889/Blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'y337kGcys&P3B'
db = SQLAlchemy(app)

#Blog class is setup to hold the main database of the blog storing things such as each
#blog title, the content of that blog and in the future likes/dislikes/comments
class Blog(db.Model):
    #current required info when creating a blog post is the blog title and text content.
    #SET LIKE/DISLIKE both to 0 when creating a post
    #left optional for weird cases where a post needs to be taken down and put back up with former like/dislike count
    #will probably break when users must be validated for likes
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(40000))
    likes = db.Column(db.Integer)
    dislikes = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    #initilizes the blog post
    #attaches a poster to each post with owner
    def __init__(self, title, body, likes, dislikes, owner):
        self.title = title
        self.body = body
        self.likes = likes
        self.dislikes = dislikes
        self.owner = owner

#user class is setup to hold data about the user        
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(28), unique=True)
    password = db.Column(db.String(28))
    blogs = db.relationship('Blog', backref='owner')
    
    #initilizes the user
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
#This makes certain pages, namely the post creation page inacessible unless you've logged into the website

@app.before_request
def require_login():
    allow_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allow_routes and 'username' not in session:
        return redirect('/login')



#the index of the page holds a directory of all users listed out
@app.route('/', methods=['POST','GET'])
def index():
    users = User.query.all()
    return render_template('index.html',title="Home Page", page_title="Home Page",users=users)
        
#renders the main blog page, pulling all items from the blog db and rendering them dynamically 
#todo- add sorting function
@app.route('/blog', methods=['POST','GET'])
def blog():
    #This sets up a few variables used throughout and looks for any query parameters
    #it then turns into some if statements that do different things depending on 
    #the query parameters
    blog_post = Blog.query.all()
    newest_post_first = Blog.query.order_by(Blog.id.desc()).all()
    #possible query params I'm looking for
    blog_id = request.args.get('id')
    add_like = request.args.get('like')
    add_dislike = request.args.get('dislike')
    user_id = request.args.get('user')
    
    #handles when a user wants to look at a specific users post history
    if request.method == 'GET' and user_id and not blog_id and not add_dislike and not add_like:
        requested_user_post = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('blog.html',title="Blog",blog=requested_user_post,page_title="Build-a-Blog")
    
    
    #when a blog id and dislike button has been clicked in html (checks if the add dislike param is true)
    #if these two parameters have been given then a dislike is added
    if request.method == 'GET' and blog_id and add_dislike and not add_like and not user_id:
        add_dislike = Blog.query.get(blog_id)
        add_dislike.dislikes = add_dislike.dislikes + 1
        db.session.commit()
        return render_template('blog.html',title="Blog",blog=newest_post_first,page_title="Build-a-Blog")   
        
    #this if statement looks to see if a blog id is given and if the user liked the post
    if request.method == 'GET' and blog_id and add_like and not add_dislike and not user_id:
        add_like = Blog.query.get(blog_id)
        add_like.likes = add_like.likes + 1
        db.session.commit()
        return render_template('blog.html',title="Blog",blog=newest_post_first,page_title="Build-a-Blog")
    
    #updates individual post likes without returning to blog
    if request.method == 'GET' and blog_id and user_id and add_like and not add_dislike:
        add_like = Blog.query.get(blog_id)
        add_like.likes = add_like.likes + 1
        db.session.commit()
        requested_post = Blog.query.get(blog_id)
        return render_template('post.html',title="Post",page_title="Blog Post",blog_title=requested_post.title,blog_content=requested_post.body,post_owner=requested_post.owner.username,owner_id=requested_post.owner_id,post_likes=requested_post.likes,post_dislikes=requested_post.dislikes,blog_id=requested_post.id)
    
    #updates individual post dislikes without returning to blog
    if request.method == 'GET' and blog_id and user_id and add_dislike and not add_like:
        add_dislike = Blog.query.get(blog_id)
        add_dislike.dislikes = add_dislike.dislikes + 1
        db.session.commit()
        requested_post = Blog.query.get(blog_id)
        return render_template('post.html',title="Post",page_title="Blog Post",blog_title=requested_post.title,blog_content=requested_post.body,post_owner=requested_post.owner.username,owner_id=requested_post.owner_id,post_likes=requested_post.likes,post_dislikes=requested_post.dislikes,blog_id=requested_post.id)
    #####
    #####
    #####
    #if statement below is suppose to handle likes/dislikes when use is viewing user page
    if request.method == 'GET' and user_id and add_like and blog_id and not add_dislike:
        add_like = Blog.query.get(blog_id)
        add_like.likes = add_like.likes + 1
        db.session.commit()
        requested_user_post = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('blog.html',title="Blog",blog=requested_user_post,page_title="Build-a-Blog")
    
    #this checks if there is only a blog id argument and then renders a page for the post clicked by the user
    if request.method == 'GET' and blog_id and not add_like and not add_dislike and not user_id:
        requested_post = Blog.query.get(blog_id)
        return render_template('post.html',title="Post",page_title="Blog Post",blog_title=requested_post.title,blog_content=requested_post.body,post_owner=requested_post.owner.username,owner_id=requested_post.owner_id,post_likes=requested_post.likes,post_dislikes=requested_post.dislikes,blog_id=requested_post.id)
    
    #this is how the page renders if no arguments are given in the url
    if request.method == 'GET':
        return render_template('blog.html',title="Blog",blog=newest_post_first,page_title="Build-a-Blog")

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
                           ,blog_post_title=blog_title,blog_post_content=blog_content,page_title="Create a Blog Post")
    
    #when the user hits the post button on the page their information is taken and
    #submitted into the database if criteria met
    if request.method == 'POST':
        blog_title = request.form['blog_post_title']
        blog_content = request.form['blog_post_content']
        owner = User.query.filter_by(username=session['username']).first()
        new_blog_post = Blog(blog_title, blog_content, 0, 0, owner) 
    
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
                           ,blog_post_title=blog_title,blog_post_content=blog_content,page_title="Create a Blog Post")

#this page handles everything to do with user signup including catching errors and commiting
#the new user to the database if they pass all validation fields
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    #error message initilization
    username_error = ""
    password_error = ""
    verify_password_error = ""
    #grabs info given if a post request is made
    if request.method == 'POST':
        username = request.form['username']
        user_pass = request.form['pass']
        user_verify_pass = request.form['verifypass']
        #if any of the required fields are left blank the user is given an error message
        #letting them know that the blank field is required
        if username == "":
            username_error="Required"
        if user_pass == "":
            password_error = "Required"
        if user_verify_pass == "":
            verify_password_error = "Required"
        #checks fields for spaces and alerts user if caught
        if " " in username:
            username_error="No Spaces Allowed"
        if " " in user_pass:
            password_error="No Spaces Allowed"
            verify_password_error ="No Spaces Allowed"  
        #checks that username and password are both greater than 3 characters
        #lets user know they must be longer if they don't meet the 3 character min
        if 3 >= len(username) and username != "" :
            username_error = "Username must be greater than 3 Characters"
        if 3 >= len(user_pass) and user_pass != "":
            password_error = "Password must be greater than 3 Characters"
        #checks that the user entered matching passwords    
        if user_pass != user_verify_pass:
            password_error = "Passwords do not match!"
            verify_password_error = "Passwords do not match!"
        #checks that no errors have been found so far and if not then
        #the user is checked in the database to make sure that username is not in use
        #if the username is not in use then the user is created and logged into the site
        #if the username is in use then the website alerts the person attempting to sign up
        #that the username they're trying to register with is already in use
        if not username_error and not password_error and not verify_password_error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username,user_pass)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/')
            else:
                username_error = "Username in use"     
    #this loads the page initially for the user
    return render_template('signup.html', title="Sign up Page", page_title="Create Account",username_error=username_error,password_error=password_error,verify_password_error=verify_password_error)

#this route handles returning users logging into the website
#with needed validation and error messages displayed to help the user
#know why their login is not working
#if it works the user is logged in and alerted that they have been logged in
@app.route('/login', methods=['POST', 'GET'])
def login():
    #page error message initization
    username_error = ""
    password_error = ""
    #runs when the user sends a post request to server
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        #if the username that the user entered is not in the database they're made aware that
        #they haven't entered a valid username
        if not user:
            flash("Username does not exist","error")
            username_error="Invalid Username"
            #rerender the page with appropriate error messages
            return render_template('login.html', title="Login Page", page_title="Log in",username_error=username_error,password_error=password_error)
        #if they entered a password that does not match the password on file
        #the user is alerted that they have not entered the correct password
        if user and user.password != password:
            flash("Incorrect Password", "error")
            password_error="Incorrect Password"
            #rerender the page with appropriate error messages
            return render_template('login.html', title="Login Page", page_title="Log in",username_error=username_error,password_error=password_error,username=username)
        #if the username exist and they have entered the password for that user correctly then
        #they are logged in and alerted that it worked
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
    #this loads the page initially for the user                               
    return render_template('login.html', title="Login Page", page_title="Log in")

#logs the user out and lets them know the action was succesfull
@app.route('/logout')
def logout():
    del session['username']
    flash("Succesfully logged out!")
    return redirect('/blog')

#standard
if __name__ == '__main__':
    app.run()