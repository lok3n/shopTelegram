from peewee import SqliteDatabase, TextField, IntegerField, Model, ForeignKeyField, DateField

db = SqliteDatabase('database.db')


class Users(Model):
    user_id = IntegerField()
    registration_date = DateField()
    name = TextField()
    username = TextField()

    class Meta:
        database = db


class Locations(Model):
    name = TextField()

    class Meta:
        database = db


class Product(Model):
    location = ForeignKeyField(model=Locations)
    photo_id = TextField()
    description = TextField()
    price = IntegerField()

    class Meta:
        database = db


class Settings(Model):
    info_text = TextField(default='empty')
    pay_text = TextField(default='empty')

    class Meta:
        database = db


class Tokens(Model):
    api = TextField()
    name = TextField()
    avaliable = IntegerField(default=1)

    class Meta:
        database = db


class Payments(Model):
    user_id = IntegerField()
    products = TextField()
    amount = IntegerField()
    message_id = IntegerField(default=0)
    finished = IntegerField(default=0)
    used_token = ForeignKeyField(model=Tokens)

    class Meta:
        database = db
