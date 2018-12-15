import bcrypt

import responder
from peewee import IntegrityError

import database
from database import db, User

api = responder.API()


@api.route('/register')
async def register(req, resp):
    @api.background.task
    def process_registration(data):
        hashed = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())
        with db:
            try:
                User.create(username=data['email'], password=hashed)
                return {'success': True}
            except IntegrityError:
                return {'error': f'A user with this email already exists: {data["email"]}'}

    if req.method == 'post':
        data = await req.media()
        resp.media = process_registration(data).result()
    else:
        resp.content = api.template('login.html', action='register')


@api.route('/login')
async def login(req, resp):
    @api.background.task
    def process_login(data):
        with db:
            user = User.get(username=data['email'])
            hashed = bcrypt.checkpw(data['password'].encode(), user.password.encode())
            if hashed:
                return {'success': True, 'username': user.username}
            return {'success': False}

    if req.method == 'post':
        data = await req.media()
        result = process_login(data).result()
        if result['success']:
            resp.session['username'] = result['username']
            resp.text = f"Logged in succesfully as {result['username']}"
        else:
            resp.text = 'Invalid username or password'
    else:
        resp.content = api.template('login.html', action='login')


@api.route("/check_logged_in")
async def check_logged_in(req, resp):
    try:
        username = req.session['username']
        with db:
            user = User.get(username=username)
            resp.text = f"You are logged in as {user.username}"
    except (KeyError, User.DoesNotExist):
        resp.text = f"You are not logged in."


@api.route("/logout")
async def logout(req, resp):
    resp.cookies["Responder-Session"] = ""
    resp.session['username'] = None
    resp.text = f"You have been logged out."

if __name__ == '__main__':
    api.run()
