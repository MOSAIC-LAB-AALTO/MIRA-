from sqlalchemy import Column, Integer, String
from database import Base

class Request(Base):
    __tablename__ = 'request'
    id = Column(Integer, primary_key=True)
    result = Column(String(50), unique=True)
    code = Column(String(120), unique=True)

    def __init__(self, code=None, result=None):
        self.result = result
        self.code = code

    def __repr__(self):
        return '<Request %r>' % (self.id)