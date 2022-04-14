import pytest
import string
import random
from flaskr import create_app
from flaskr.forms import RegistrationForm, LoginForm
from flaskr.db import UserDB

headers = {'Content-Type': 'application/json'}
app = create_app()
app.config['WTF_CSRF_ENABLED'] = False
c = app.test_client()
with c.session_transaction() as sess:
        sess['imagecode'] = '11'

""" we perform our test on user "zyk" """
test_uid = UserDB.select().where(UserDB.username == "zyk")
if len(test_uid) == 0:
    with app.test_request_context():
        register_form = RegistrationForm(
            username="zyk",
            password="zykzykzyk", 
            confirm_password="zykzykzyk",
            email="zyksir@gmail.com",
            imagecode="11"
        )
        c.post("/auth/register", data=register_form.data, follow_redirects=True)
        test_uid = UserDB.select(UserDB.id).where(UserDB.username == "zyk")
test_uid = test_uid.get().id

def string_in_page(str_list, page):
    if isinstance(str_list, str):
        str_list = [str_list]
    for string in str_list:
        if string not in page:
            return False, string
    return True, ""

def check_get(url, expected_string):
    response = c.get(url)
    status_code, resp_data = response.status_code, str(response.data)
    assert status_code == 200, f"{url} GET Error: {status_code}"
    ok, err_string = string_in_page(expected_string, resp_data)
    # if "ViewPost" in url:
    #     print(resp_data)
    assert ok, f"{url} GET Error: {err_string} not exists in return content"

def check_post(url, expected_string, request, unexpected_string=None):
    response = c.post(url, data=request, follow_redirects=True)
    status_code, resp_data = response.status_code, str(response.data)
    assert status_code == 200, f"{url} Post Error: {status_code}"
    ok, err_string = string_in_page(expected_string, resp_data)
    # if "/auth/login" in url and "Type" in err_string:
    #     print(resp_data)
    assert ok, f"{url} POST Error: {err_string} not exists in return content"
    if unexpected_string is not None:
        ok, err_string = string_in_page(unexpected_string, resp_data)
        print(resp_data)
        assert not ok, f"{url} POST Error: {unexpected_string} is in return content"

def test_register():
    check_get(url="/auth/register", 
              expected_string=["Username", "Password", "Email", "Verification", "Register"])

    with app.test_request_context():
        register_form = RegistrationForm(
            username="zyk",
            password="zykzykzyk", 
            confirm_password="zykzykzyk",
            email="zyksir@gmail.com",
            imagecode="13"
        )
        check_post(url="/auth/register", request=register_form.data,
                expected_string="Imagecode Incorrect")
        register_form.imagecode.data = "11"
        check_post(url="/auth/register", request=register_form.data,
                expected_string="is already registered.")

        # a randomly generated username to make sure it's new
        username = str(random.randint(0, 9)).join(random.sample(string.ascii_letters, 6))
        register_form.username.data = username
        check_post(url="/auth/register", 
                request=register_form.data,
                expected_string="Login</button>")

def test_login():
    check_get(url="/auth/login",
              expected_string="Login</button>")

    with app.test_request_context():
        login_form = LoginForm(
            username="zyk",
            password="zykzykzyk", 
            imagecode="13"
        )
        check_post(url="/auth/login", 
                    request=login_form.data,
                    expected_string=["Imagecode Incorrect"])
        login_form.imagecode.data = "11"
        login_form.password.data = "test_zyk"
        check_post(url="/auth/login", 
                    request=login_form.data,
                    expected_string=["Password Incorrect", "Login</button>"])
        login_form.password.data = "zykzykzyk"
        login_form.username.data = "t"
        check_post(url="/auth/login", 
                    request=login_form.data,
                    expected_string=["Username Does Not Exist"])
        login_form.username.data = "zyk"
        check_post(url="/auth/login", 
                    request=login_form.data,
                    expected_string=["Type", "City", "Start", "End", "Search"])

def test_valid_code():
    _ = c.get("/auth/code")
    with c.session_transaction() as sess:
        assert sess['imagecode'] != "11111", "imagecode is too simple"
        sess['imagecode'] = "11"

def test_user_profile():
    with c.session_transaction() as sess:
        sess['user_id'] = test_uid
    check_get(url=f"/user/home/{test_uid}",
              expected_string=["zyk", "zyksir@gmail.com", "Recent Published"])
    
def test_set_user_profile():
    with c.session_transaction() as sess:
        sess['user_id'] = test_uid
    
    check_get(url=f"/user/set", expected_string=["Update"])

    set_request = {"email" : "zyk_test@gmail.com"}
    check_post(url=f"/user/set",  request=set_request,
              expected_string=["zyk", "zyk_test@gmail.com"])
    set_request = {"email" : "zyksir@gmail.com"}
    check_post(url=f"/user/set",  request=set_request,
              expected_string=["zyk", "zyksir@gmail.com"])
    set_request = {"nowpass" : "zykzykzykzyk", "password": "zykzykzyk","repassword": "zykzykzyk"}
    check_post(url=f"/user/set",  request=set_request,
              expected_string=["Wrong password"])

def test_create_pet():
    with c.session_transaction() as sess:
        sess['user_id'] = test_uid
    pet_type = random.choice(["dog", "cat"])
    city = random.choice(["Los Angeles", "San Diego", "Philadelphia", "New York"])
    age, weight, description = 1, 10, "cute dog"
    if pet_type == "dog":
        age, weight, description = random.choice([
            (1, 10, "Affenpinscher"), 
            (4, 50, "AfghanHounds"), 
            (4, 20, "Shiba Inu")
        ])
    create_request = {"age": age, "weight": weight, "type": pet_type, "description": description, "city": city,
                      "startdate": "2021-12-11", "enddate": "2021-12-19"}
    check_post(url="/create", request=create_request, expected_string="")

    create_request = {"age": 2, "weight": 15, "type": "dog", "description": "husky", "city": "Los Angeles",
                      "startdate": "2022-11-1", "enddate": "2021-12-1"}
    check_post(url="/create", request=create_request, expected_string="Oops! End date should be after start date :)")

def test_main_page():
    check_get(url=f"/",
              expected_string=["Type:", "City", "Start", "End", "Publish a New Post"])
    
    check_get(url="/ViewPost/1", expected_string="Type")
    reply_request = {'body': 'test reply', 'author_id': 28}
    check_post(url="/ViewPost/1", request=reply_request, expected_string="test reply")

def test_search_page():
    check_post(url=f"/", request={"type": "cat"},
                expected_string=["cat"], unexpected_string="dog")
    check_post(url=f"/", request={"startdate": "2021-11-30", "enddate": "2021-11-01"},
                expected_string=["End date should be after start date"])


    



    
    

