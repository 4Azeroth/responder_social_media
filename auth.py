from database import User, db


def get_current_user(req):
    try:
        user_id = req.session['user_id']
        username = req.session['username']
        with db:
            return User.get(id=user_id, username=username)
    except (KeyError, User.DoesNotExist):
        return None
