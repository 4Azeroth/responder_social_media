from contextlib import suppress

import bcrypt

import responder
from peewee import IntegrityError

from auth import get_current_user
from database import db, User, UserPost

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
        user = get_current_user(req)
        if user:
            resp.status_code = 303
            resp.headers['Location'] = "/"
        else:
            resp.content = api.template('login.html', action='register')


@api.route('/login')
async def login(req, resp):
    @api.background.task
    def process_login(data):
        with db:
            with suppress(User.DoesNotExist):
                user = User.get(username=data['email'])
                hashed = bcrypt.checkpw(data['password'].encode(), user.password.encode())
                if hashed:
                    return {'success': True, 'user_id': user.id, 'username': user.username}
            return {'success': False, 'error': 'Invalid email address or password'}

    if req.method == 'post':
        data = await req.media()
        result = process_login(data).result()
        if result['success']:
            resp.session.update({'user_id': result['user_id'], 'username': result['username']})
            resp.text = f"Logged in succesfully as {result['username']}"
            resp.status_code = 303
            resp.headers['Location'] = "/"
        else:
            resp.content = api.template('login.html', action='login', error=result['error'])
    else:
        user = get_current_user(req)
        if user:
            resp.status_code = 303
            resp.headers['Location'] = "/"
        else:
            resp.content = api.template('login.html', action='login')


@api.route("/")
async def home_screen(req, resp):
    user = get_current_user(req)
    posts = UserPost.select().where(UserPost.user in [user]).order_by(UserPost.date.desc())
    resp.content = api.template('home.html', user=user, posts=posts)


@api.route("/post")
async def post(req, resp):
    @api.background.task
    def process_post(data):
        nonlocal req
        user = get_current_user(req)
        with db:
            UserPost.create(user=user, content=data['content'])
        return

    data = await req.media()
    process_post(data).result()
    resp.status_code = 303
    resp.headers['Location'] = "/"


@api.route("/check_logged_in")
async def check_logged_in(req, resp):
    user = get_current_user(req)
    if user:
        resp.text = f"You are logged in as {user.username}"
    else:
        resp.text = f"You are not logged in."


@api.route("/logout")
async def logout(req, resp):
    resp.cookies["Responder-Session"] = ""
    resp.session.update({'user_id': None, 'username': None})
    resp.status_code = 303
    resp.headers['Location'] = "/"

if __name__ == '__main__':
    api.run()
