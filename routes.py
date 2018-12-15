import responder;
from database import db, User;

api = responder.API()


@api.route('/{username}')
def test_route(req, resp, *, username):
    with db:
        User.get_or_create(
            username=username
        )
    resp.text = f"Thanks for visiting {username}!"


if __name__ == '__main__':
    api.run()
