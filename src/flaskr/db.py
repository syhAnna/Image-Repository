# -*- coding: utf-8 -*-
# author: zyk
# create a connection to it. Any queries and operations are performed using the connection
# define tables that need to be used

import sys
from collections import defaultdict
from flask import current_app, g
from flask.cli import with_appcontext
import json
import datetime
from peewee import *

try:
    dbConfig = json.load(open("flaskr/dbConfig.json"))
except:
    dbConfig = json.load(open("../flaskr/dbConfig.json"))
mydatabase = MySQLDatabase(host=dbConfig["host"],
                        user=dbConfig["user"],
                        passwd=dbConfig["passwd"],
                        database=dbConfig["database"],
                        charset="utf8",
                        port=3306)
mydatabase.connect()

class BaseModel(Model):
    class Meta:
        database = mydatabase

class ImageDB(BaseModel):
    created = DateTimeField(default=datetime.datetime.now)
    filename = TextField()
    filehash = TextField(null=True)

# peewee will generate an auto-increment field id for every db
class UserDB(BaseModel):
    created = DateTimeField(default=datetime.datetime.now)
    username = CharField(unique=True)
    password = CharField()
    email = CharField()
    image = ForeignKeyField(ImageDB, null=True, default=None)

class PetDB(BaseModel):
    owner = ForeignKeyField(UserDB, backref="owner_id", column_name="owner_id")
    age = IntegerField(default=0)
    weight = IntegerField(default=0)
    created = DateTimeField(default=datetime.datetime.now)
    type = TextField()
    location = TextField()
    description = TextField()
    image = ForeignKeyField(ImageDB, null=True, default=None)
    startdate = DateTimeField()
    enddate = DateTimeField()

class ReplyDB(BaseModel):
    author = ForeignKeyField(UserDB, backref="author_id", column_name="author_id")
    pet = ForeignKeyField(PetDB, backref="pet_id", column_name="pet_id")
    created = DateTimeField(default=datetime.datetime.now)
    body = TextField()

mydatabase.create_tables([UserDB, PetDB, ReplyDB, ImageDB])
if ImageDB.select().count() < 2:
    ImageDB.insert({
        ImageDB.filename: "default_image.jpeg",
        ImageDB.created: datetime.datetime.now()
    }).execute()
    ImageDB.insert({
        ImageDB.filename: "default_dog_image.gif",
        ImageDB.created: datetime.datetime.now()
    }).execute()
def init_app(app):
    return
