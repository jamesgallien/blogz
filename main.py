from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:MyNewPass@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'somestring'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    entry = db.Column(db.String(120))

    def __init__(self, title, entry):
        self.title = title
        self.entry = entry

@app.route('/', methods=['GET'])
def index():

    return redirect('/blog')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_entry = request.form['entry']
        if len(blog_title) == 0 or len(blog_entry) == 0:
            flash("Both fields are required", "error")
            return redirect('/newpost')

        new_blog = Blog(blog_title, blog_entry)    
        db.session.add(new_blog)    
        db.session.commit()
        id = new_blog.id

        return redirect('/blog?id=' + str(id))

        # blogs = Blog.query.all() # filter_by(completed=False)    
        # # completed_tasks = Task.query.filter_by(completed=True).all()
        # return render_template('blog.html',title="Build a Blog",     
        #         blogs=blogs) # completed_tasks=completed_tasks)    
    
    return render_template('newpost.html', title="Add a Blog Entry")

@app.route('/blog', methods=['GET'])
def blog():   
    
    # completed_tasks = Task.query.filter_by(completed=True).all()
    if request.args:
        blog = Blog.query.filter_by(id=request.args.get('id')).first()
        blog_title = blog.title
        blog_entry = blog.entry
        return render_template('blog.html', blog_title=blog_title, blog_entry=blog_entry, title=blog_title)

    blogs = Blog.query.all() # filter_by(completed=False)
    return render_template('blog.html', blogs=blogs, title="Build a Blog") # completed_tasks=completed_tasks)


# @app.route('/delete-task', methods=['POST'])
# def delete_task():

#     task_id = int(request.form['task-id'])
#     task = Task.query.get(task_id)
#     task.completed = True
#     db.session.add(task)
#     db.session.commit()

#     return redirect('/')


if __name__ == '__main__':
    app.run()