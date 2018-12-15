from peewee import *

# SQLite database using WAL journal mode and 64MB cache.
db = SqliteDatabase('./app.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1024 * 64})


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField()


with db:
    db.create_tables([User])