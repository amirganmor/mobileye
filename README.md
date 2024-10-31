# Project Setup Guide

This guide outlines the steps required to set up the PostgreSQL database and run the REST API server locally on macOS using FastAPI.
## Project Structure
- `intuit_final.py`: Contains the main application code, including endpoints for fetching all players and fetching a player by ID.
- `Dockerfile`: Docker configuration file to containerize the application.
- `requirements.txt`: Lists the Python dependencies for the project.
- `test_intuit_final.py`: Contains unit tests for the API using `pytest`.

## Step 1: Install PostgreSQL

1. **Using Homebrew**  
   If you have Homebrew installed, use it to install PostgreSQL by running the following commands in your terminal:
   ```bash
   brew update
   brew install postgresql



2. **Initialize and Start PostgreSQL**

    ```bash
    brew services start postgresql
    ```

Optionally, initialize the database (only if PostgreSQL hasn't been initialized before):
    ```bash
   initdb /usr/local/var/postgres
    ```

3. **Create a Database and User**
Enter the PostgreSQL command line interface to create a database and user:
    ```bash
    psql postgres
    ```

## Step 2: Create Database and Tables


1. **Create the Database**
    Inside the psql interface, create a database:
    ```bash
    CREATE DATABASE mlm;
    ```

2. **Switch to the New Database**
    Connect to the newly created database:
    ```bash
    \c mlm;
    ```
3. **Create Tables**
Run the following SQL commands to create the users, books, and checkouts tables:
    ```sql
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(100) NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE
    );

    CREATE TABLE books (
        id SERIAL PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        author VARCHAR(100) NOT NULL,
        available BOOLEAN DEFAULT TRUE
    );

    CREATE TABLE checkouts (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        book_id INTEGER REFERENCES books(id),
        checkout_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        due_date TIMESTAMP,
        returned BOOLEAN DEFAULT FALSE
    );
    ```
## Step 3: Setting Up the REST API on macOS

1. **Navigate to the Project Directory**
Open your terminal and navigate to your project directory:
    ```bash
    cd <WORKING_DIR>
    ```
2. **Create and Activate the Virtual Environment**
Create a virtual environment for the project and activate it:
    ```bash
    python3 -m venv venv_mobileye
    source venv_mobileye/bin/activate
    ```
3. **Install Requirements**
With the virtual environment activated, install the necessary dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. **Run the REST API Server**
Start the server in development mode:
    ```bash
    uvicorn main:app --reload
    ```
The server should now be running locally at http://127.0.0.1:8000.

### API Documentation
FastAPI provides interactive API documentation interfaces accessible at localhost:

1. **Swagger UI**
A user-friendly, interactive API documentation interface:
http://127.0.0.1:8000/docs

2. **ReDoc**
An alternative API documentation interface with a clean design:
http://127.0.0.1:8000/redoc