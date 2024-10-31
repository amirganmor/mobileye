import pytest
from unittest.mock import Mock, patch

# Mocking the database functions
mock_db = {
    'books': [{'id': 1, 'author': 'Author Name', 'title': 'Test Book', 'checked_out': False}],
    'users': []
}

# Mock functions to replace database access
def mock_get_db():
    return mock_db

# Simulated Flask routes for testing
def add_book(book):
    book_id = len(mock_db['books']) + 1
    book['id'] = book_id
    mock_db['books'].append(book)
    return {'id': book_id}, 201

def get_books():
    return mock_db['books'], 200

def remove_book(book_id):
    global mock_db
    mock_db['books'] = [book for book in mock_db['books'] if book['id'] != book_id]
    return {'message': 'Book removed'}, 200

def checkout_book(book_id):
    for book in mock_db['books']:
        if book['id'] == book_id:
            book['checked_out'] = True
            return {'checked_out': True}, 200
    return {'message': 'Book not found'}, 404

def return_book(book_id):
    for book in mock_db['books']:
        if book['id'] == book_id:
            book['checked_out'] = False
            return {'checked_out': False}, 200
    return {'message': 'Book not found'}, 404

# Tests
def test_add_book():
    new_book = {'author': 'New Author', 'title': 'New Test Book'}
    response, status_code = add_book(new_book)
    assert status_code == 201
    assert response['id'] == 2
    assert len(mock_db['books']) == 2

def test_get_books():
    response, status_code = get_books()
    assert status_code == 200
    assert len(response) == 2  # 1 existing + 1 added in previous test

def test_remove_book():
    response, status_code = remove_book(1)
    assert status_code == 200
    assert response['message'] == 'Book removed'
    assert len(mock_db['books']) == 1  # Only 1 book left

def test_checkout_book():
    response, status_code = checkout_book(1)
    assert status_code == 404

def test_return_book():
    response, status_code = return_book(1)
    assert status_code == 404

if __name__ == '__main__':
    pytest.main()
