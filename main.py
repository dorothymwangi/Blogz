from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "123blogz"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(600))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password 


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        if user and user.password != password:
            flash('User password incorrect', 'error')
        if not user:
            flash('User does not exist', 'error')
    return render_template('login.html')               


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        #validate user's data
        if len(username) <3 or " " in username:
            flash('Username must have at least 3 characters','error')
            return redirect ('/signup')

        if ("@" not in username) or ("." not in username):
            flash('Please enter a valid email address','error') 
            return redirect ('/signup')   

        if len(password) <3 or " " in password:
            flash('Password must have at least 3 characters','error')
            password =''
            return redirect ('/signup')
            
        if verify != password:
            flash('Passwords do not match','error')
            verify=''
            return redirect ('/signup')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('Username already exists','error')
            return redirect ('/login')
            
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)
   
@app.route('/blog')
def blog():
    if request.args:
        blog_id = request.args.get('id')
        owner_id = request.args.get('id')
        #user_id = Blog.query.filter_by(owner_id=session['owner_id']).first()
        #user_id = owner_id
        blog = Blog.query.get(blog_id) 
        user = Blog.query.get(owner_id)

        #if Blog.query.get('/blog?id='+str(blog_id)):     
        return render_template('individualblog.html', blog=blog, user=user)            
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', title='Blogs', blogs=blogs)    
    
    #blogger_id = Blog.query.get('owner_id')

   # user=User.query.get('/user?id='+ str(user.id))
   
#@app.route('/newpost')
#def index():
  #  return render_template('newpost.html', title='Build a Blog') 

@app.route('/newpost', methods = ['POST','GET'])
def newpost():
    
    if request.method == 'GET':
        return render_template('newpost.html', title='Blogz')

    if request.method == 'POST':
        blog_title = request.form['blog']
        blog_body = request.form['body']
        owner_id = User.query.filter_by(username=session['username']).first()
        blog_title_error = ""
        blog_body_error = ""
        
        if blog_title == "":
            blog_title_error="Please enter a blog title"
        if blog_body == "":
            blog_body_error="Please enter blog content"

        if not blog_title_error and not blog_body_error:
            new_blog = Blog(blog_title, blog_body, owner_id)
            db.session.add(new_blog)
            db.session.commit() 

            blog=Blog.query.get('/blog?id='+ str(new_blog.id))

            return render_template('individualblog.html', blog=new_blog)
            #return redirect('/blog')
        else:
            return render_template('newpost.html',blog=blog_title, body=blog_body, 
            blog_title_error=blog_title_error, blog_body_error=blog_body_error)       
    
if __name__ =='__main__':
    app.run()
