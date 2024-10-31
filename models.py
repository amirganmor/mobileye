# models.py
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import func  # Import func for default timestamp

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_admin = Column(Boolean, default=False)
    
    checkouts = relationship("Checkout", back_populates="user")

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    available = Column(Boolean, default=True)

class Checkout(Base):
    __tablename__ = 'checkouts'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    checkout_date = Column(TIMESTAMP, server_default=func.now())  # Set default to current timestamp
    due_date = Column(TIMESTAMP)
    returned = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="checkouts")
    book = relationship("Book")