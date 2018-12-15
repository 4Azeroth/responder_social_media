from database import User, db, Friend


def get_current_user(req):
    try:
        user_id = req.session['user_id']
        username = req.session['username']
        with db:
            return User.get(id=user_id, username=username)
    except (KeyError, User.DoesNotExist):
        return None


def get_friends(user):
    with db:
        friends = Friend.select().where(Friend.user == user)
    return [friend.friend for friend in friends]
