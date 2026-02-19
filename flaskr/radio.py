from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from mutagen.mp3 import MP3

from flaskr.auth import login_required
from flaskr.db import get_db

import os

bp = Blueprint('radio', __name__)



@bp.route('/')
def index():
    # db = get_db()
    # posts = db.execute(
    #     'SELECT p.id, title, body, created, author_id, username'
    #     ' FROM post p JOIN user u ON p.author_id = u.id'
    #     ' ORDER BY created DESC'
    # ).fetchall()
    # return render_template('radio/index.html', posts=posts)

    return render_template('radio/index.html')


ALLOWED_EXTENSIONS = {"mp3"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/admin', methods=('GET', 'POST'))
@login_required
def admin():

    db = get_db()

    if request.method == 'POST':
        if "file" not in request.files:
            return "No file part", 400

        file = request.files["file"]

        if file.filename == "":
            return "No selected file", 400
        
        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)

            save_path = os.path.join(current_app.config["TRACK_FOLDER"], filename)
            print("ZZZZZZZZZZZZZ", save_path)
            file.save(save_path)

            try:
                audio = MP3(save_path)
                duration = audio.info.length
                print("Duration:", duration)
            except Exception:
                os.remove(save_path)
                return "Invalid MP3 file", 400
            
            db.execute(
                "INSERT INTO track (filename) VALUES (?)",
                (filename,)
            )

            db.commit()
            
        else:
            return "Invalid file type", 400
        
    tracks = db.execute(
        f'SELECT CONCAT(\'{current_app.config["TRACK_FOLDER"]}/\', filename)'
        'FROM track'
    ).fetchall()



    return render_template('radio/admin.html', tracks=tracks)

# @bp.route('/')
# def index():
#     db = get_db()
#     posts = db.execute(
#         'SELECT p.id, title, body, created, author_id, username'
#         ' FROM post p JOIN user u ON p.author_id = u.id'
#         ' ORDER BY created DESC'
#     ).fetchall()
#     return render_template('blog/index.html', posts=posts)

# @bp.route('/create', methods=('GET', 'POST'))
# @login_required
# def create():
#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required.'

#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'INSERT INTO post (title, body, author_id)'
#                 ' VALUES (?, ?, ?)',
#                 (title, body, g.user['id'])
#             )
#             db.commit()
#             return redirect(url_for('blog.index'))

#     return render_template('blog/create.html')

# def get_post(id, check_author=True):
#     post = get_db().execute(
#         'SELECT p.id, title, body, created, author_id, username'
#         ' FROM post p JOIN user u ON p.author_id = u.id'
#         ' WHERE p.id = ?',
#         (id,)
#     ).fetchone()

#     if post is None:
#         abort(404, f"Post id {id} doesn't exist.")

#     if check_author and post['author_id'] != g.user['id']:
#         abort(403)

#     return post

# @bp.route('/<int:id>/update', methods=('GET', 'POST'))
# @login_required
# def update(id):
#     post = get_post(id)

#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required.'

#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'UPDATE post SET title = ?, body = ?'
#                 ' WHERE id = ?',
#                 (title, body, id)
#             )
#             db.commit()
#             return redirect(url_for('blog.index'))

#     return render_template('blog/update.html', post=post)

# @bp.route('/<int:id>/delete', methods=('POST',))
# @login_required
# def delete(id):
#     get_post(id)
#     db = get_db()
#     db.execute('DELETE FROM post WHERE id = ?', (id,))
#     db.commit()
#     return redirect(url_for('blog.index'))