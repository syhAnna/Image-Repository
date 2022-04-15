import os
import logging

from werkzeug.exceptions import ExpectationFailed
from .db import *
from .util import *
from werkzeug.utils import secure_filename
from playhouse.shortcuts import model_to_dict
from werkzeug.security import check_password_hash

class ImageInfo:
    """ This class encapsulates all the relevant operations related to image file.
    """

    @staticmethod
    def get_image_by_id(image_id):
        """given a unique image id, retrieve all the relevant information about the image.

        :param image_id: the unique image id
        :type image_id: int
        :return: a dictionary of all the information about an image, including filename location, created time, and file hash value
        :rtype: dictionary
        """        
        image = model_to_dict(ImageDB.select().where(ImageDB.id == image_id).get())
        if image_id > 2:
            image["filename"] = os.path.join(UPLOAD_FOLDER, str(image_id) + "_" + image["filename"])
        else:
            image["filename"] = os.path.join("/static/pic/", image["filename"])
        logging.info(f"get_image_by_id({image_id}) returns {image}")
        return image
    
    @staticmethod
    def add_new_image(file, savepath):
        """add a new image to the database, and will get the unique image id.

        :param file: the image file
        :type file: FILE type, can retrieve content and filename from it
        :param savepath: the local relevant saving path
        :type savepath: string
        :return: unique image id
        :rtype: int
        """        
        file_content = file.read()
        logging.info(f"add_new_image {file.filename}")
        filename = secure_filename(file.filename)
        filehash = generate_filecont_hash(file_content)

        image_id = ImageDB.insert({
            ImageDB.filename: filename, 
            ImageDB.filehash: filehash
        }).execute()

        file_path = os.path.join(savepath, str(image_id) + "_" + filename)
        with open(file_path, "wb") as fw:
            fw.write(file_content)
        logging.info("Save %s to %s" % (filename, file_path))
        return image_id
    
    @staticmethod
    def delete_image(image_id):
        """given the unique image id, delete the record related to the image in the database

        :param image_id: unique image id in the database
        :type image_id: int
        """        
        ImageDB.delete().where(ImageDB.id == image_id)

class UserInfo:
    """ The class representing a User, and provides all the relevant operations with database.
    """    
    def __init__(self, uid=-1, uname="", pets = [],
                 image=None, email=None, register_date=None):
        self.uid = uid
        self.email = email
        self.uname = uname
        self.register_date = register_date
        self.pets = pets
        self.uimage = image

    @staticmethod
    def add_new_user(username, password, email):
        """Add a new user with the given information to the database

        :param username: the new user's username
        :type username: string
        :param password: the new user's password
        :type password: string
        :param email: the new user's email
        :type email: string
        :return: the new user's unique id
        :rtype: int
        """        
        uid = UserDB.insert({
            UserDB.username: username,
            UserDB.password: password,
            UserDB.email: email,
            UserDB.created: datetime.datetime.now(),
            UserDB.image_id: 1
        }).execute()
        return uid
    
    @staticmethod
    def get_login_info(form, correct_imagecode):
        """Get user information stored in database with the given form that contains username, password and the verification code if the verification code and password matches. Otherwise, return null user information and error message.

        :param form: contains username, password, imagecode
        :type form: dictionary
        :param correct_imagecode: this will be used to compared with the imagecode in the form
        :type correct_imagecode: string
        :return: user_info(the user information stored in database, if doesn't exist or match failure, return none), error (if error occur, return error message, otherwise return None)
        :rtype: dictionary / None, string / None
        """        
        username = form['username']
        password = form['password']
        imagecode = form['imagecode']
        error = None
        user_info = UserDB.select().where(UserDB.username == username)
        if len(user_info) == 0:
            error = "Error: Username Does Not Exist"
            user_info = None
        else:
            user_info = user_info.get()
            logging.info(f"input password {password}, password in db {user_info.__dict__}")
            if not check_password_hash(user_info.password, password):
                error = "Error: Password Incorrect"
            elif imagecode != correct_imagecode:
                error = "Error: Imagecode Incorrect"
        return user_info, error

    @staticmethod
    def get_user_info_by_uid(uid):
        """Get user information of given user id

        :param uid: user's unique id
        :type uid: int
        :return: all the user's information (including the pets information) if retrieve from database successfully, otherwise return None
        :rtype: dictionary / None
        """        
        try:
            uinfo = model_to_dict(UserDB.select(UserDB.id, UserDB.username, UserDB.email, UserDB.created, UserDB.image_id).where(UserDB.id == uid).get())
        except Exception as err_msg:
            logging.info(f"ERROR: fail to get user info with {err_msg}")
            return None
        logging.info(f"get user info {uinfo}")
        pets = PetInfo.get_pets_by_uid(uid)
        image = ImageInfo.get_image_by_id(image_id=uinfo["image"]["id"])
        uinfo["image"] = image["filename"]
        uinfo["pets"] = pets
        return uinfo 
    
    @staticmethod
    def get_user_info_by_username(username):
        """Get user information of given username

        :param username: user's username
        :type username: string
        :return: all the user's information (including the pets information) if retrieve from database successfully, otherwise return None
        :rtype: dictionary / None
        """        
        try:
            uinfo = model_to_dict(UserDB.select(UserDB.id, UserDB.password).where(UserDB.username == username).get())
        except Exception as err_msg:
            logging.info(f"ERROR: fail to get user info with {err_msg}")
            return None
        logging.info(f"get user info {uinfo}")
        return uinfo 
    
    @staticmethod
    def check_if_username_exist(username):
        """chechs whether the username already exists in the database

        :param username: the proposed username
        :type username: string
        :return: whether the username exists in the database
        :rtype: boolean
        """        
        return len(UserDB.select(UserDB.id).where(UserDB.username == username)) > 0

class PetInfo:
    """The class representing a pet, and provides all the relevant operations with database.
    """    
    def __init__(self, pid=-1, plocation="", pstart=None, pend=None,
                    pweight=-1, p_age=-1, ptype = "",
                    pdescription="", pimage = None):
        self.pid = pid
        self.p_age = p_age
        self.ptype = ptype
        self.pweight = pweight
        self.pimage = pimage
        self.plocation = plocation
        self.pdescription = pdescription
        self.pstart = pstart
        self.pend = pend
    
    @staticmethod
    def add_new_pet(form, file):
        """Add a new pet with the given information to the database if the date range is valid. Otherwise, return error message.

        :param form: the information about the pet, contains owner id, age, weight, type, city, description, startdate, enddate
        :type form: dictionary
        :param file: the image file of the pet
        :type file: FILE type
        :return: pet_id (the unique pet id), error (error message if date range is not valid)
        :rtype: int / None, None / string
        """        
        image_id = 1
        if file is not None and file.filename:
            savepath = form["savepath"]
            if not os.path.exists(savepath):
                os.mkdir(savepath)
            image_id = ImageInfo.add_new_image(file, savepath)
        elif "dog" in form["type"].lower():
            image_id = 2

        pet_id, error = None, ""
        startdate = datetime.datetime.strptime(form["startdate"], "%Y-%m-%d")
        enddate = datetime.datetime.strptime(form["enddate"], "%Y-%m-%d")
        logging.info(f"create pet with image id:{image_id}")
        if (enddate - startdate).days < 0:
            error = "Oops! End date should be after start date :)"
        else:
            pet_id = PetDB.insert({
                PetDB.image_id: image_id,
                PetDB.owner_id: form["owner_id"],
                PetDB.age: form["age"],
                PetDB.weight: form["weight"],
                PetDB.type: form["type"].lower(),
                PetDB.location: form["city"].lower(),
                PetDB.description: form["description"],
                PetDB.startdate: startdate,
                PetDB.enddate: enddate
            }).execute()

        return pet_id, error

    @staticmethod
    def get_pets_by_uid(uid):
        """Get all the owned pet information of a given user id

        :param uid: user's unique id
        :type uid: int
        :return: a list of the user's pets information
        :rtype: list
        """        
        pets = []
        raw_pets = PetDB.select(PetDB.id, PetDB.age, PetDB.weight, PetDB.type,
                                PetDB.created, PetDB.description, PetDB.image_id)\
                                .where(PetDB.owner_id == uid).order_by(PetDB.created.desc())
        for pet in raw_pets:
            pet = model_to_dict(pet)
            image = ImageInfo.get_image_by_id(image_id=pet["image"]["id"])
            pet["image"] = image["filename"]
            pets.append(pet)
        return pets   

    @staticmethod
    def get_pets(form={}):
        """return the pets information in the database that satisfies given requirements in the form if the date range is valid. Otherwise, return error message

        :param form: contains filter requirement, like type, city, startdate, enddate, defaults to {}
        :type form: dict, optional
        :return: pets (a list of all the pets information), error (error message if the date range is invalid)
        :rtype: list, string / None
        """        
        error = None
        ptype, pcity = "%%", "%%"
        if "type" in form:
            ptype = "%" + form["type"] + "%"
        if "city" in form:
            pcity = "%" + form["city"] + "%"
        pstartdate, penddate = datetime.datetime.strptime("2000-1-1", "%Y-%m-%d"), datetime.datetime.strptime("3000-1-1", "%Y-%m-%d")
        if "startdate" in form and form["startdate"]:
            pstartdate = datetime.datetime.strptime(form["startdate"], "%Y-%m-%d")
        if "enddate" in form and form["enddate"]:
            penddate = datetime.datetime.strptime(form["enddate"], "%Y-%m-%d")
        if (penddate - pstartdate).days < 0:
            error = "Oops! End date should be after start date :)"
            pstartdate, penddate = datetime.datetime.strptime("2000-1-1", "%Y-%m-%d"), datetime.datetime.strptime("3000-1-1", "%Y-%m-%d")
        allpets = PetDB.select().where(PetDB.type ** ptype, PetDB.location ** pcity, PetDB.startdate > pstartdate, PetDB.enddate < penddate).order_by(PetDB.created.desc())
        pets = []
        for pet in allpets:
            pet = model_to_dict(pet)
            logging.info(f"image_id is {pet['image']['id']} for {pet['id']}")
            image = ImageInfo.get_image_by_id(image_id=pet["image"]["id"])
            logging.info(image)
            pet["image"] = image["filename"]
            pet["owner"].pop("password")
            pet["owner"].pop("image")
            pets.append(pet)
        logging.info(f"posts: {pets[:5]}")
        return pets, error

    @staticmethod
    def get_pet_for_view(pet_id):
        """Get the pet information given a unique pet id

        :param pet_id: the unique pet id
        :type pet_id: int
        :return: all the information related to the pet
        :rtype: dictionary
        """        
        pet = model_to_dict(PetDB.select().where(PetDB.id == pet_id).get())
        pet["username"] = pet["owner"]["username"]
        pet["owner_id"] = pet["owner"]["id"]
        pet.pop("owner")
        image = ImageInfo.get_image_by_id(image_id=pet["image"]["id"])
        pet["image"] = image["filename"]
        pet["reply"] = ReplyInfo.get_reply_by_pid(pet_id)
        return pet
    
    @staticmethod
    def delete_pet(pet_id):
        """Delete a certain pet's information in the database

        :param pet_id: the unique pet id
        :type pet_id: int
        """        
        image_id = PetDB.select(PetDB.image_id).where(PetDB.id == pet_id).get()
        ImageInfo.delete_image(image_id)
        ReplyInfo.delete_reply_by_pet_id(pet_id)
        PetDB.delete().where(PetDB.id == pet_id).execute()


class ReplyInfo:
    """The class representing a reply message, and provides all the relevant operations with database.
    """    
    @staticmethod
    def get_reply_by_pid(pet_id):
        """Get all the replies related to a pet

        :param pet_id: the unique pet id
        :type pet_id: int
        :return: all the replies for the pet
        :rtype: list
        """        
        allreplys = ReplyDB.select().where(ReplyDB.pet_id == pet_id)
        replys = []
        for reply in allreplys:
            reply = model_to_dict(reply)
            reply['username'] = reply["author"]["username"]
            reply.pop("author")
            reply.pop("pet")
            replys.append(reply)
        return replys
    
    @staticmethod
    def add_reply(form, pet_id):
        """add a reply to the pet

        :param form: contains all the information related to the reply, like the reply content, and the creator
        :type form: dictionary
        :param pet_id: unique pet id that the reply is targeted for
        :type pet_id: int
        :return: the unique reply id
        :rtype: int
        """        
        reply_id = ReplyDB.insert(body=form["body"], author_id=form['author_id'], pet_id=pet_id).execute()
        return reply_id
    
    @staticmethod
    def delete_reply(reply_id):
        """delete a certain reply

        :param reply_id: the unique reply id
        :type reply_id: int
        """        
        ReplyDB.delete().where(ReplyDB.id == reply_id).execute()
    
    @staticmethod
    def delete_reply_by_pet_id(pet_id):
        """delete all the replies related to a pet

        :param pet_id: the unique pet id
        :type pet_id: int
        """        
        ReplyDB.delete().where(ReplyDB.pet_id == pet_id).execute()
    

