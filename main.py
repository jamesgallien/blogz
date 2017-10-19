from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'somestring'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    entry = db.Column(db.String(120))
    # relationship here
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, entry, owner):
        self.title = title
        self.entry = entry
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    # relationship here
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'index', 'signup', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['GET','POST'])
def index():

    users = User.query.all()
    return render_template('index.html', users=users, title="Authors")

    #return redirect('/blog')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username:
            error = "Please enter a value"
            return render_template("login.html", username_error=error, username=username)

        if not password:
            error = "Please enter a value"
            return render_template("login.html", password_error=error, username=username)

        user = User.query.filter_by(username=username).first()
        
        if user:
            if user.password == password:
                session['username'] = username
                flash("Logged in")
                return redirect('/newpost')
            else:
                error = "Incorrect password"
                return render_template('login.html', password_error=error, username=username)
        else:
            error = "Username does not exist"
            return render_template("login.html", username_error=error, username=username)

    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify_password']

        if not username:
            error = "Please enter a value"
            return render_template("signup.html", username_error=error, username=username)

        if not password:
            error = "Please enter a value"
            return render_template("signup.html", password_error=error, username=username)

        if (len(username) < 3):
            error = "Invalid username"
            return render_template("signup.html", username_error=error, username=username)

        if (len(password) < 3):
            error = "Invalid password"
            return render_template("signup.html", password_error=error, username=username)

        if not verify_password:
            error = "'Password' and 'Verify password' are required fields"
            return render_template("signup.html", password_error=error, p_verify_error=error, username=username)
        
        if password != verify_password:
            error = "Passwords must match"
            return render_template("signup.html", password_error=error, p_verify_error=error, username=username)    

        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username

            #return render_template('welcome.html, name=name)

            return redirect('/newpost')
        else:
            error = "Usernanme already exists"
            return render_template("signup.html", username_error=error, username=username)

    return render_template('signup.html')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        
        blog_title = request.form['title']
        blog_entry = request.form['entry']
        if len(blog_title) == 0 or len(blog_entry) == 0:
            flash("Both fields are required", "error")
            return render_template('newpost.html', blog_title=blog_title, blog_entry=blog_entry, title="Add a Blog Entry")

        owner_id = User.query.filter_by(username=session['username']).first()

        new_blog = Blog(blog_title, blog_entry, owner_id)    
        db.session.add(new_blog)
        db.session.commit()
        id = new_blog.id
        return redirect('/blog?id=' + str(id))

    return render_template('newpost.html', title="Add a Blog Entry")

@app.route('/blog', methods=['GET'])
def blog():   
    
    # if request.args:
    if request.args.get('id'):
        blog = Blog.query.filter_by(id=request.args.get('id')).first()
        user = User.query.filter_by(id=blog.owner_id).first()
        blog_title = blog.title
        blog_entry = blog.entry
        return render_template('blog.html', blog_title=blog_title, blog_entry=blog_entry, title=blog_title, user=user)

    elif request.args.get('user'):
        user = User.query.filter_by(id=request.args.get('user')).first()
        blogs = Blog.query.filter_by(owner_id=request.args.get('user'))
        # blog_title = blog.title
        # blog_entry = blog.entry
        return render_template('author_posts.html', blogs=blogs, title="Blog posts!", user=user)
        
    blogs = Blog.query.all()
    users = User.query.all()
    return render_template('blog.html', blogs=blogs, users=users, title="All blogs")

@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()