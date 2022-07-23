from peewee import *


db = SqliteDatabase('database/database.db')

class BaseModel(Model):
    id = PrimaryKeyField()

    class Meta:
        database = db

class Film(BaseModel):
    title = CharField()
    description = CharField(null=True)
    code = CharField()
    message_id = IntegerField()


class User(BaseModel):
    user_id = IntegerField()
    premium = BooleanField(default=False)
    limit = IntegerField()
    random_last = IntegerField(default=0)
    last = IntegerField(default=0)

    def down_limit(self):
        self.limit = self.limit - 1
        self.save()

    def up_limit(self, num):
        self.limit = self.limit + num
        self.save()

    def set_last(self, time):
        self.last = time
        self.save()

    def set_random_last(self, time):
        self.random_last = time
        self.save()


class Config(BaseModel):
    start_limit = IntegerField()
    one_day = IntegerField()
    one_week = IntegerField()
    price = IntegerField()

    def edit_start_limit(self, new: int):
        self.start_limit = new
        self.save()

    def edit_one_day(self, new: int):
        self.one_day = new
        self.save()

    def edit_one_week(self, new: int):
        self.one_week = new
        self.save()

    def edit_price(self, new: int):
        self.price = new
        self.save()

class Channel(BaseModel):
    title = CharField()
    chat_id = IntegerField()
    url = CharField()
    active = BooleanField(default=True)


def test():
    pass


if __name__ == '__main__':
    test()
