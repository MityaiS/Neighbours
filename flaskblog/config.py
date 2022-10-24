import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DB_NAME = "site.db"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + DB_NAME
    MAIL_SERVER = 'smtp.mail.ru'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = "dmitrix_n@mail.ru" 
    MAIL_PASSWORD = "b3mLFnxNrxRfKGA2uqfw"
