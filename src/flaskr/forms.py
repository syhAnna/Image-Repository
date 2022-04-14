# -*- coding: utf-8 -*-
# author: Fan Yin
# Registration and login forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=1, max=40)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=16)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    imagecode = StringField('Verification code', validators = [DataRequired()])
    register = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username',
                        validators=[DataRequired(), Length(min=1, max=40)])
    # email = StringField('Email',
    #                     validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    imagecode = StringField('Verification code', validators = [DataRequired()])
    submit = SubmitField('Login')