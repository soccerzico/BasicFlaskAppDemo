
// Show/hide add book form
function toggleAddBook() {
    const form = document.getElementById("addBookForm");

    if (form.style.display === "block") {
        form.style.display = "none";
    } else {
        form.style.display = "block";
    }
}

// Show/hide search form
function toggleSearch() {
    const form = document.getElementById("searchForm");

    if (form.style.display === "block") {
        form.style.display = "none";
    } else {
        form.style.display = "block";
    }
}

// Add a book to the database
function addBook() {
    const bookTitle = document.getElementById('bookTitle').value;
    const publicationYear = document.getElementById('publicationYear').value;
    const bookAuthor = document.getElementById('bookAuthor').value;
    const imageUrl = document.getElementById('imageUrl').value;

    const bookData = {
        title: bookTitle,
        publication_year: publicationYear,
        author: bookAuthor,
        url: imageUrl
    };

    fetch('/api/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(bookData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error adding book:', data.error);
                return;
            }

            books.push(bookData);

            showAddSuccessPopup(bookData);

            clearAddBookForm();

            // Optional: close form after submit
            document.getElementById("addBookForm").style.display = "none";

            // Optional: refresh shelf after adding
            showAllBooks();
        })
        .catch(error => {
            console.error('Error adding book:', error);
        });
}

// Clear add-book form fields
function clearAddBookForm() {
    document.getElementById('bookTitle').value = '';
    document.getElementById('publicationYear').value = '';
    document.getElementById('bookAuthor').value = '';
    document.getElementById('imageUrl').value = '';
}

// Popup after successful add
function showAddSuccessPopup(book) {
    const popup = window.open("", "Book Added", "width=450,height=550");

    popup.document.write(`
        <html>
        <head>
            <title>Book Added</title>
            <style>
                body {
                    font-family: Roboto, sans-serif;
                    text-align: center;
                    padding: 20px;
                    color: #2b1b12;
                }
                img {
                    margin-top: 12px;
                    border-radius: 10px;
                    box-shadow: 0 8px 18px rgba(0,0,0,0.35);
                }
                h2 {
                    margin-bottom: 10px;
                }
                button {
                    margin-top: 20px;
                    padding: 8px 14px;
                    border: none;
                    border-radius: 6px;
                    background-color: #5c3d2e;
                    color: white;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <h2>Book Added Successfully</h2>
            <h3>${book.title}</h3>
            <p><strong>Author:</strong> ${book.author}</p>
            <p><strong>Publication Year:</strong> ${book.publication_year}</p>
            <img src="${book.url}" alt="Book cover" width="180" height="260">
            <br>
            <button onclick="window.close()">Close</button>
        </body>
        </html>
    `);
}

// Reusable renderer for books on the page
function renderBooks(bookArray, containerId) {
    const bookList = document.getElementById(containerId);
    bookList.innerHTML = '';

    bookArray.forEach(book => {
        const bookElement = document.createElement('div');
        bookElement.classList.add('book');

        bookElement.innerHTML = `
            <h2>${book.title}</h2>
            <p>Publication Year: ${book.publication_year}</p>
            <p>Author: ${book.book_author || book.author}</p>
            <img src="${book.url}" alt="Book cover" width="160" height="220">
        `;

        bookList.appendChild(bookElement);
    });
}

// Fetch and display all books from server
function showAllBooks() {
    fetch('/api/books')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error fetching all books:', data.error);
                return;
            }

            renderBooks(data.books, 'allbooks');
        })
        .catch(error => {
            console.error('Error fetching all books:', error);
        });
}

// Search books using Flask backend route
function searchBooks() {
    const searchValue = document.getElementById('searchInput').value.trim();

    fetch(`/api/search?q=${encodeURIComponent(searchValue)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error searching books:', data.error);
                return;
            }

            showSearchResultsPopup(data.books, searchValue);
        })
        .catch(error => {
            console.error('Error searching books:', error);
        });
}

// Show search results in popup
function showSearchResultsPopup(results, searchValue) {
    const popup = window.open("", "Search Results", "width=600,height=700");

    popup.document.write(`
        <html>
        <head>
            <title>Search Results</title>
            <style>
                body {
                    font-family: Roboto, sans-serif;
                    padding: 20px;
                    color: #2b1b12;
                    text-align: center;
                }
                .result-book {
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #ccc;
                }
                img {
                    margin-top: 10px;
                    border-radius: 10px;
                    box-shadow: 0 8px 18px rgba(0,0,0,0.35);
                }
                button {
                    margin-top: 20px;
                    padding: 8px 14px;
                    border: none;
                    border-radius: 6px;
                    background-color: #5c3d2e;
                    color: white;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <h2>Search Results</h2>
            <p><strong>Search term:</strong> ${searchValue}</p>
    `);

    if (results.length === 0) {
        popup.document.write(`<p>No results found.</p>`);
    } else {
        results.forEach(book => {
            popup.document.write(`
                <div class="result-book">
                    <h3>${book.title}</h3>
                    <p><strong>Author:</strong> ${book.book_author}</p>
                    <p><strong>Publication Year:</strong> ${book.publication_year}</p>
                    <img src="${book.url}" alt="Book cover" width="160" height="240">
                </div>
            `);
        });
    }

    popup.document.write(`
            <button onclick="window.close()">Close</button>
        </body>
        </html>
    `);
}

// Function to add a review
function addReview() {
    const bookId = document.getElementById('bookId').value;
    const userName = document.getElementById('userName').value;
    const rating = document.getElementById('rating').value;
    const comment = document.getElementById('comment').value;

    const reviewData = {
        book_id: bookId,
        user: userName,
        rating: rating,
        comment: comment
    };

    fetch('/api/add_review', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(reviewData)
    })
        .then(response => response.json())
        .then(data => {
            console.log(data.message); 
        })
        .catch(error => {
            console.error('Error adding review:', error);
        });
}

// Function to fetch and display all reviews
function showAllReviews() {
    fetch('/api/reviews')
        .then(response => response.json())
        .then(data => {
            const reviewList = document.getElementById('reviewList');
            reviewList.innerHTML = '';  // Clear existing reviews

            data.reviews.forEach(review => {
                const reviewElement = document.createElement('div');
                reviewElement.classList.add('review');
                reviewElement.innerHTML = `
                    <h3>Book ID: ${review.book_id}</h3>
                    <p>User: ${review.user}</p>
                    <p>Rating: ${review.rating}</p>
                    <p>Comment: ${review.comment}</p>
                `;
                reviewList.appendChild(reviewElement);
            });
        })
        .catch(error => {
            console.error('Error fetching reviews:', error);
        });
}

