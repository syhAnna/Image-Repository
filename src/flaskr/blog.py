# main page
# 1. show posts in the nearby location
# 2. show 
from logging import log
from flask import (
    Blueprint, flash, g, session, redirect, render_template, request, url_for, current_app
)
from .info import *
from .util import *
from .auth import login_required
from flask_paginate import Pagination


bp = Blueprint('blog', __name__)

# index page
@bp.route("/",methods=('GET', 'POST'))
@bp.route('/<int:page>')
def index(page=None):
    form = {}
    if request.method == 'POST':
        form = request.form
        logging.info(f"get pets with {form}")
    all_pets, error = PetInfo.get_pets(form=form)
    if error:
        flash(error)
    if page is None or (page-1)*6 >= len(all_pets):
        page = 1
    pagination = Pagination(page=page, per_page=6, total=len(all_pets), css_framework="foundation")
    s, e = (page-1)*6, min(page*6, len(all_pets))
    # logging.info(f"pagination: {pagination.__dict__}")
    return render_template('blog/index.html', posts=all_pets[s:e], pagination=pagination)


# create a new post
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        form = dict(request.form)
        form["savepath"] = current_app.config['UPLOAD_FOLDER']
        form["owner_id"] = g.user['id']
        file = request.files.get("photo", default=None)
        logging.info(f"request.form for create {form}, {request.files}")
        pet_id, error = PetInfo.add_new_pet(form, file=file)
        if not error:
            return redirect(url_for('blog.index'))
        flash(error)

    return render_template('blog/create.html')

@bp.route('/ViewPost/<int:pet_id>', methods=('GET', 'POST'))
def ViewPost(pet_id):
    if request.method == 'POST':
        form = dict(request.form)
        form["author_id"] = g.user['id']
        logging.info(f"reply form is {form}")
        ReplyInfo.add_reply(form, pet_id)

    pet = PetInfo.get_pet_for_view(pet_id)
    logging.info(f"info of pet is {pet}")
    return render_template('blog/ViewPost.html', post=pet)


# Not implement yet
# delete a reply by id
@bp.route('/DeleteReply/<int:id>', methods=('POST',))
@login_required
def DeleteReply(id):
    post_id = ReplyInfo.delete_reply(id)
    return redirect(url_for('blog.ViewPost', id=post_id))


@bp.route('/DeletePost/<int:id>', methods=('POST',))
@login_required
def DeletePost(id):
    PetInfo.delete_pet(id)
    return redirect(url_for('blog.index'))
