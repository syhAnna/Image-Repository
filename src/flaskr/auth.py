import re
import functools
import logging

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)

from werkzeug.security import generate_password_hash
from .info import *
from .util import *
from io import BytesIO
from .forms import RegistrationForm, LoginForm


# A Blueprint is a way to organize a group of related views and other code.
# Rather than registering views and other code directly with an application,
# they are registered with a blueprint.
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Fan: modify the register() and login() function call with flask-wtf, now display all error messages at one time and
# and on the same page.
@bp.route('/register', methods=('GET', 'POST'))
def register():
    forms = RegistrationForm()
    if request.method =='POST' and forms.validate():
        username = forms.username.data
        password = generate_password_hash(forms.password.data)
        email = forms.email.data
        imagecode = forms.imagecode.data
        if not session['imagecode'] == imagecode:
            code_error = 'Error: Imagecode Incorrect'
            return render_template('auth/register.html', form=forms, code_error=code_error)
        if UserInfo.check_if_username_exist(username):
            use_error = 'Error: User {} is already registered.'.format(username)
            return render_template('auth/register.html', form=forms, use_error=use_error)
        UserInfo.add_new_user(username=username, password=password, email=email)
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=forms)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        # logging.info(request.form)
        username = form.username.data
        password = form.password.data
        imagecode = form.imagecode.data
        if imagecode != session['imagecode']:
            code_error = "Error: Imagecode Incorrect"
            return render_template('auth/login.html', form=form, code_error=code_error)
        if not UserInfo.check_if_username_exist(username):
            use_error = "Error: Username Does Not Exist"
            return render_template('auth/login.html', form=form, user_error=use_error)
        user_info = UserInfo.get_user_info_by_username(username)
        logging.info(f"input password {password}, password in db {user_info}")
        if not check_password_hash(user_info["password"], password):
            pwd_error = "Error: Password Incorrect"
            return render_template('auth/login.html', form=form, pwd_error=pwd_error)
        session.clear()
        session['user_id'] = user_info["id"]
        return redirect(url_for('index'))
    return render_template('auth/login.html', form=form)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = UserInfo.get_user_info_by_uid(user_id)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            redirect(url_for('blog.index'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/code')
def get_code():
    # Write binary format image into the memory, release the space in disk
    image, str = generate_validate_picture()
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    # send binary image as respond to the frontend and set the header
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/gif'
    # save image code as string into the session
    session['imagecode'] = str
    return response
