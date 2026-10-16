from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()


# -----------------------------
# Starting data
# -----------------------------

books = [
    {
        "id": 1,
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "category": "Programming",
        "available": True
    },
    {
        "id": 2,
        "title": "Atomic Habits",
        "author": "James Clear",
        "category": "Self Help",
        "available": False
    }
]


# -----------------------------
# Pydantic Model
# -----------------------------

class Book(BaseModel):
    title: str
    author: str
    category: str
    available: bool


# -----------------------------
# GET - All Books
# -----------------------------

@app.get("/books")
def get_books(
    category: str | None = None,
    available: bool | None = None
):
    result = books

    # Filter by category
    if category:
        result = [
            book for book in result
            if book["category"].lower() == category.lower()
        ]

    # Filter by availability
    if available is not None:
        result = [
            book for book in result
            if book["available"] == available
        ]

    return result


# -----------------------------
# GET - Single Book
# -----------------------------

@app.get("/books/{book_id}")
def get_book(book_id: int):

    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(
        status_code=404,
        detail="Book not found"
    )


# -----------------------------
# POST - Add Book
# -----------------------------

@app.post("/books")
def add_book(book: Book):

    # Generate new ID
    if len(books) == 0:
        new_id = 1
    else:
        new_id = max(book["id"] for book in books) + 1

    new_book = {
        "id": new_id,
        "title": book.title,
        "author": book.author,
        "category": book.category,
        "available": book.available
    }

    books.append(new_book)

    return new_book


# -----------------------------
# PUT - Update Book
# -----------------------------

@app.put("/books/{book_id}")
def update_book(book_id: int, updated_book: Book):

    for book in books:

        if book["id"] == book_id:

            book["title"] = updated_book.title
            book["author"] = updated_book.author
            book["category"] = updated_book.category
            book["available"] = updated_book.available

            return book

    raise HTTPException(
        status_code=404,
        detail="Book not found"
    )


# -----------------------------
# DELETE - Delete Book
# -----------------------------

@app.delete("/books/{book_id}")
def delete_book(book_id: int):

    for book in books:

        if book["id"] == book_id:

            books.remove(book)

            return {
                "message": "Book deleted successfully",
                "book": book
            }

    raise HTTPException(
        status_code=404,
        detail="Book not found"
    )