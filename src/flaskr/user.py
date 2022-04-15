from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
import logging

from .auth import login_required
from pprint import pprint
from .db import *
from .info import *
from playhouse.shortcuts import model_to_dict
from flask_paginate import Pagination

bp = Blueprint('user', __name__, url_prefix='/user')

""" get user_info """
@bp.route('/home/<string:user_id>')
@bp.route('/home/<string:user_id>/<int:page>',methods=('GET', 'POST'))
def home(user_id, page=None):
    user_info = UserInfo.get_user_info_by_uid(user_id)
    logging.info(f"user info for {user_id}: {user_info}")
    all_pets = user_info["pets"]
    if page is None or (page-1)*20 >= len(all_pets):
        page = 1
    pagination = Pagination(page=page, per_page=20, total=len(all_pets), css_framework="foundation")
    s, e = (page-1)*20, min(page*20, len(all_pets))
    user_info["pets"] = all_pets[s:e]
    return render_template('user/home.html', user=user_info, pagination=pagination)

@bp.route('/set', methods=('GET', 'POST'))
def set():
    if request.method == 'POST':
        if 'email' in request.form:
            email = request.form['email']
            t = UserDB.update(email=email).where(UserDB.id == g.user['id'])
            t.execute()
            return redirect(url_for('user.home', user_id=g.user['id']))
        elif 'password' in request.form:
            nowpass = request.form['nowpass']
            password = request.form['password']
            repassword = request.form['repassword']
            real_password = model_to_dict(UserDB.select(UserDB.password).where(UserDB.id == g.user['id']).get())['password']
            error = None
            if not password:
                error = 'Password is required.'
            elif not (password ==repassword):
                error = 'Two passwords are inconsistent.'
            elif not (password == repassword):
                error = 'you enter different passwords!'
            elif ((len(password) < 6) or (len(password) > 16)):
                error = 'The length of password should be between 6 and 16.'
            elif not (check_password_hash(real_password, nowpass)):
                error = 'Wrong password!'

            if error is not None:
                flash(error)
            else:
                t = UserDB.update(password=generate_password_hash(password)).where(UserDB.id == g.user['id'])
                t.execute()
                return redirect(url_for('user.home', user_id=g.user['id']))
        else:
            savepath = current_app.config['UPLOAD_FOLDER']
            file = request.files.get("photo", default=None)
            if file is not None and file.filename:
                if not os.path.exists(savepath):
                    os.mkdir(savepath)
                image_id = ImageInfo.add_new_image(file, savepath)
                t = UserDB.update(image_id=image_id).where(UserDB.id == g.user['id'])
                t.execute()
                return redirect(url_for('user.home', user_id=g.user['id']))
            else:
                error = 'Fail to upload File'
                flash(error)

    return render_template('user/easy_set.html')

