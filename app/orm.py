# sqlalchmy orm for user and image tables

from sqlalchemy import Column, String, Integer, create_engine, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# create object for base class
Base = declarative_base()

# define user object

class DBSession(object):
    def __init__(self, path_to_db='sqlite:///db.sqlite3'):
        self.engine = create_engine(path_to_db)
        DBSession = sessionmaker(bind=self.engine)
        self.session = DBSession()

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
    
    def generate_all(self):
        Base.metadata.create_all(self.engine)


class User(Base):
    # table name
    __tablename__ = 'user'

    # table structure
    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String(20))
    email = Column(String(20), unique=True)
    password = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)

    def __str__(self):
        return self.name
    
    def save(self):
        db = DBSession()
        with db as session:
            session.add(self)
            session.commit()
    
    @classmethod
    def get(cls, id):
        with DBSession() as db:
            return db.query(cls).filter_by(id=id).first()
    
    @classmethod
    def get_by_email(cls, email):
        with DBSession() as db:
            return db.query(cls).filter_by(email=email).first()
    
    @classmethod
    def get_all(cls):
        with DBSession() as db:
            return db.query(cls).all()
    
    @classmethod
    def delete(cls, id):
        db = DBSession()
        with db as session:
            session.delete(cls.get(id))
            session.commit()

# define image object
class Image(Base):
    # table name
    __tablename__ = 'image'

    # table structure
    id = Column(Integer, primary_key=True,autoincrement=True)
    user_id = Column(Integer)
    file_name = Column(String(50))
    file_path = Column(String(50))
    emotion = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)

    def __str__(self):
        return self.file_name

    def save(self):
        db = DBSession()
        with db as session:
            session.add(self)
            session.commit()

    @classmethod
    def get(cls, id):
        with DBSession() as db:
            return db.query(cls).filter_by(id=id).first()

    @classmethod
    def get_by_user(cls, user_id):
        with DBSession() as db:
            return db.query(cls).filter_by(user_id=user_id).all()

    @classmethod
    def get_all(cls):
        with DBSession() as db:
            return db.query(cls).all()

    @classmethod
    def delete(cls, id):
        db = DBSession()
        with db as session:
            session.delete(cls.get(id))
            session.commit()


    