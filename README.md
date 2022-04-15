### About ImageRepository -- CatEatPad
#### main Structure
##### FrontEnd 
The source code of FrontEnd is in `flaskr/templates`. 
##### BackEnd 
- `auth.py`: code for login and register
- `blog.py`: code for main page, creating post and comment
- `user.py`: code for user profile
##### Database 
- `info.py`: create a API of modifying database 
- `db.py`: define table and connect with MySQL

#### how to Run CatEatPad
##### download mysql
- for this [this link](https://dev.mysql.com/doc/refman/8.0/en/macos-installation-pkg.html) to download mysql in mac
- add `export PATH="/usr/local/mysql-8.0.27-macos11-x86_64/bin/:$PATH"` in `~/.bashrc`
- run `mysql -u root -p` in terminal, create a database named "CatEatPad" by executing `CREATE DATABASE CatEatPad;`

##### run
- run `bash start.sh` in `src` dictionary 
- theoretically every library we need should be contained by `venv`, if you want to pip install something,  please remember to run `. venv/bin/activate` first
- add `dbConfig.json` under `src/flaskr/` 
```json
{
    "host": "127.0.0.1",
    "user": "root",
    "passwd": "YourPassWord",
    "database": "CatEatPad"
}
```

##### test
- run `pytest` in `src` to test. more more details, see [testing in Flask](https://flask.palletsprojects.com/en/2.0.x/testing/)

##### How to run on Windows:
- First, install the required packages as indicated before, using   `py -m pip install *`
- Then, use the cmd command:
```
set FLASK_ENV=development
set FLASK_DEBUG=1
set FLASK_APP=flaskr
py -m flask run
```

#### about Flask
- [Learn Flask for Python(youtube)](https://www.youtube.com/watch?v=Z1RJmh_OqeA)
