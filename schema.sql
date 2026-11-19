-- Enable Foreign Key constraints in SQLite
PRAGMA foreign_keys = ON;

-- Drop tables if they already exist (clean reset)
DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS members;

-- 1. Members Table
CREATE TABLE members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    joined_date DATE NOT NULL
);

-- 2. Books Table
CREATE TABLE books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    category TEXT NOT NULL,
    total_copies INTEGER NOT NULL CHECK (total_copies >= 0)
);

-- 3. Loans Table (Transaction / Relationship Table)
CREATE TABLE loans (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    issue_date DATE NOT NULL,
    return_date DATE,
    status TEXT NOT NULL CHECK (status IN ('Issued', 'Returned')),
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

-- Indexing for faster JOIN and filtering performance
CREATE INDEX idx_loans_member ON loans(member_id);
CREATE INDEX idx_loans_book ON loans(book_id);
CREATE INDEX idx_loans_status ON loans(status);

-- Insert Sample Data into Members
INSERT INTO members (full_name, email, joined_date) VALUES
('Abhishek Mishra', 'abhishek.m@invertis.ac.in', '2026-08-10'),
('Prajjwal Bajpai', 'prajjwal.b@invertis.ac.in', '2026-08-12'),
('Aryan verma', 'aryan.s@invertis.ac.in', '2026-08-15'),
('kaushal Gangwar', 'kaushal.t@invertis.ac.in', '2026-08-18'),
('laki chauhan', 'laki.k@invertis.ac.in', '2026-08-20');

-- Insert Sample Data into Books
INSERT INTO books (title, author, category, total_copies) VALUES
('Database System Concepts', 'Abraham Silberschatz', 'Database', 5),
('Clean Code', 'Robert C. Martin', 'Software Engineering', 4),
('Introduction to Algorithms', 'Thomas H. Cormen', 'Algorithms', 3),
('Learning SQL', 'Alan Beaulieu', 'Database', 6),
('Python Crash Course', 'Eric Matthes', 'Programming', 4);

-- Insert Sample Data into Loans
INSERT INTO loans (member_id, book_id, issue_date, return_date, status) VALUES
(1, 1, '2026-09-01', '2026-09-10', 'Returned'),
(1, 4, '2026-09-12', NULL, 'Issued'),
(2, 1, '2026-09-03', NULL, 'Issued'),
(2, 2, '2026-09-05', '2026-09-14', 'Returned'),
(3, 3, '2026-09-07', NULL, 'Issued'),
(4, 1, '2026-09-09', '2026-09-16', 'Returned'),
(4, 5, '2026-09-15', NULL, 'Issued'),
(5, 4, '2026-09-18', NULL, 'Issued');