from datetime import datetime

from peewee import *

# SQLite database using WAL journal mode and 64MB cache.
db = SqliteDatabase('./app.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1024 * 64})


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = AutoField(primary_key=True)
    username = CharField(unique=True)
    password = CharField()


class UserPost(BaseModel):
    id = AutoField(primary_key=True)
    user = ForeignKeyField(model=User)
    content = CharField()
    date = DateTimeField(default=datetime.now)


with db:
    db.create_tables([User, UserPost])
