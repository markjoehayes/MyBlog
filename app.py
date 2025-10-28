import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort



def get_db_connection():
    """creates database connection and sets up row factory 
        for name-based column access"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    # open the connection to the db
    conn = get_db_connection()
    # select the post base on it's id
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    # close the connection
    conn.close()
    # checking if we already have the post or not
    if post is None:
        abort(404)
    return post

def get_comments(post_id):
    conn = get_db_connection()
    comments = conn.execute(
            'SELECT * FROM comments WHERE post_id = ? ORDER BY created DESC',
            (post_id,)
    ).fetchall()
    conn.close()
    return comments

def add_comments(post_id, author, content):
    conn = get_db_connection()
    conn.execute(
            'INSERT INTO comments(post_id, author, content) VALUES (?,?,?)',
            (post_id, author, content)
            )
    conn.commit()
    conn.close()

# create an instance of a flask app and name it app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define a view function for creation
@app.route('/create', methods=('GET', 'POST'))
def create():
    # if the user clicked on submit, it sends the post request
    if request.method == 'POST':
        # Get the title and save it in a variable
        title = request.form['title']
        # Get the content and save it in a variable
        content = request.form['content']
        if not title:
            flash('Title is required')
        else:
            # open a connection to db
            conn = get_db_connection()
            # insert the new values in the db
            conn.execute('INSERT INTO posts(title, content) VALUES (?,?)', (title, content))
            conn.commit()
            conn.close()
            # redirect the user to the index page
            return redirect(url_for('index'))

    return render_template('create.html')

# Define a view function for the main route '/'
@app.route('/')  # decorator associates the function with the root URL
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/<int:post_id>')
def post(post_id):
    # we got the post the user clicked on through the function we wrote before
    # we save the value of the post in the post variable
    post = get_post(post_id)
    # include comments
    comments = get_comments(post_id)
    # we render the post page, pass post variable as an argument to use in the html page
    return render_template('post.html', post=post, comments=comments)

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    # Get the post to be edited by its id
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            # Update the table
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash(f'"{post['title']}" was successfully deleted!')
    return redirect(url_for('index'))

@app.route('/<int:post_id>/comment', methods=('POST',))
def add_comment_route(post_id):
    author = request.form['author']
    content = request.form['content']

    if not author or not content:
        flash('Both name and comment are required!')
    else:
        add_comments(post_id, author, content)
        flash('Conmment added successfuly!')

    return redirect(url_for('post', post_id = post_id))

# add route to delete comments (admin only)
@app.route('/comment/<int:comment_id>/delete')
def delete_comment(comment_id):
    conn = get_db_connection()
    comment = conn.execute('SELECT * FROM comments WHERE id = ?', (comment_id,)).fetchone()
    if comment:
        conn.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
        conn.commit()
        flash('Comment deleted!')
    conn.close()
    return redirect(url_for('post', post_id=comment['post_id']))
  
