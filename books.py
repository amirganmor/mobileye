# books.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Book, User, Checkout
from schemas import BookCreate, BookOut
from typing import List
import datetime
from utils import trim_string
import logging

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Add a new book (admin only)
@router.post("/books/", response_model=BookOut)
def add_book(book: BookCreate, db: Session = Depends(get_db)):
    try:
        book.title = trim_string(book.title)  # Trim whitespace
        book.author = trim_string(book.author)  # Trim whitespace
        db_book = Book(**book.dict())
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        logger.info(f"Book added: {db_book.title} by {db_book.author}")
        return db_book
    except Exception as e:
        logger.error(f"Error adding book: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error adding book: {str(e)}")

# Remove a book (admin only)
@router.delete("/books/{book_id}", response_model=BookOut)
def remove_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    try:
        db.delete(db_book)
        db.commit()
        logger.info(f"Book removed: {db_book.title} by {db_book.author}")
        return db_book
    except Exception as e:
        logger.error(f"Error removing book: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error removing book: {str(e)}")

# Get all books with optional filters
@router.get("/books/", response_model=List[BookOut])
def get_books(author: str = None, title: str = None, available: bool = None, db: Session = Depends(get_db)):
    # Trim optional filter inputs
    if author:
        author = trim_string(author)
    if title:
        title = trim_string(title)
    query = db.query(Book)
    
    if author:
        query = query.filter(Book.author == author)
    if title:
        query = query.filter(Book.title == title)
    if available is not None:
        query = query.filter(Book.available == available)
    books = query.all()
    logger.info(f"Retrieved {len(books)} books with filters - Author: {author}, Title: {title}, Available: {available}")
    return books

# Checkout a book
@router.post("/checkout/{book_id}", response_model=BookOut)
def checkout_book(book_id: int, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    book = db.query(Book).filter(Book.id == book_id).first()
    
    if not user:
        logger.warning(f"Checkout attempt for non-existent user: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    if not book:
        logger.warning(f"Checkout attempt for non-existent book: {book_id}")
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Limit the number of books a user can checkout to 10
    if len(user.checkouts) >= 10:
        logger.warning(f"User {user.id} has reached the maximum checkout limit.")
        raise HTTPException(status_code=400, detail="User has already checked out the maximum number of books")
    
    try:
        due_date = datetime.datetime.now() + datetime.timedelta(days=14)  # Set due date to 14 days from now
        new_checkout = Checkout(user_id=user.id, book_id=book.id, due_date=due_date)
        db.add(new_checkout)
        db.commit()
        db.refresh(new_checkout)
        logger.info(f"Book checked out: {book.title} by {user.username} with due date {due_date}")
        return book
    except Exception as e:
        logger.error(f"Error checking out book: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error checking out book: {str(e)}")

# Return a book
@router.post("/return/{book_id}")
def return_book(book_id: int, user_id: int, db: Session = Depends(get_db)):
    user_id = trim_string(str(user_id))
    book_id = trim_string(str(book_id))

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    checkout_entry = db.query(Checkout).filter(
        Checkout.user_id == user.id,
        Checkout.book_id == book_id,
        Checkout.returned == False
    ).first()

    if not checkout_entry:
        logger.warning(f"Return attempt for a book not checked out by user {user_id}: {book_id}")
        raise HTTPException(status_code=404, detail="Checkout entry not found or book not checked out")

    try:
        checkout_entry.returned = True
        db.commit()
        logger.info(f"Book returned: {checkout_entry.book_id} by user {user.username}")
        return {"message": "Book returned successfully"}
    except Exception as e:
        logger.error(f"Error returning book: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error returning book: {str(e)}")

# Get checked out books for a user
@router.get("/checked-out/")
def get_user_checked_out_books(user_id: int, db: Session = Depends(get_db)):
    user_id = trim_string(str(user_id))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Checked out books request for non-existent user: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    checked_out_books = db.query(Checkout).filter(
        Checkout.user_id == user.id,
        Checkout.returned == False
    ).all()

    books = []
    for checkout in checked_out_books:
        book = db.query(Book).filter(Book.id == checkout.book_id).first()
        if book:
            books.append(book)

    logger.info(f"User {user_id} has checked out {len(books)} books.")
    return books

# Admin endpoint to see all checked-out books
@router.get("/admin/checked-out/", response_model=List[BookOut])
def get_all_checked_out_books(db: Session = Depends(get_db)):
    checked_out_records = db.query(Checkout).filter(Checkout.returned == False).all()

    checked_out_books = []
    for record in checked_out_records:
        book = db.query(Book).filter(Book.id == record.book_id).first()
        if book:
            checked_out_books.append(book)
    logger.info(f"Admin retrieved {len(checked_out_books)} checked out books.")
    return checked_out_books

# Check fines for a user
@router.get("/fines/")
def check_fines(user_id: int, db: Session = Depends(get_db)):
    user_id = trim_string(str(user_id))
        
    checkouts = db.query(Checkout).filter(
        Checkout.user_id == user_id,
        Checkout.returned == False
    ).all()
    
    total_fine = 0.0

    for checkout in checkouts:
        if checkout.due_date < datetime.datetime.utcnow():  # Check if the book is overdue
            overdue_days = (datetime.datetime.utcnow() - checkout.due_date).days
            total_fine += overdue_days * 0.10  # 10 cents per overdue day
    logger.info(f"Total fine checked for user {user_id}: {total_fine}")
    return {"total_fine": total_fine}
