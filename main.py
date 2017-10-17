from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(600))
    
    def __init__(self, name, body):
        self.name = name
        self.body = body

@app.route('/blog')
def blog():
    blogs = Blog.query.all()
    blog_id = request.args.get('id')
    
    blog_name = request.args.get('name')
    blog_body = request.args.get('body')
    
    #return indv_blog

    #return blog_id
    #if request.args.get('id'):
    if blog_id:  
        indv_blog = Blog.query.filter_by(blog_id)   
        return render_template('/individualblog.html',blog=indv_blog, blog_name=blog_name, blog_body=blog_body)
            
    else:
        return render_template('blog.html', title='My blogs', blogs=blogs)    

@app.route('/newpost')
def index():
    return render_template('newpost.html', title='Build a Blog') 

@app.route('/newpost', methods = ['POST'])
def newpost():
    #if request.method == 'POST':
    blog_name = request.form['blog']
    blog_body = request.form['body']
    blog_name_error = ""
    blog_body_error = ""

    if blog_name == "":
        blog_name_error="Please enter a blog name"
    if blog_body == "":
        blog_body_error="Please enter blog content"

    if not blog_name_error and not blog_body_error:
        new_blog = Blog(blog_name, blog_body)
        db.session.add(new_blog)
        db.session.commit() 
        return redirect('/blog')
    else:
        return render_template('newpost.html',blog=blog_name, body=blog_body, 
           blog_name_error=blog_name_error, blog_body_error=blog_body_error)
    
@app.route('/individualblog')
def single():
    blog = request.args.get('blog')
    body = request.args.get('body')
    return render_template ('individualblog.html', blog=blog, body=body)

if __name__ =='__main__':
    app.run()
