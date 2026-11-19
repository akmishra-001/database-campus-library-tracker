# Campus Library & Book Lending Tracker

## 1. Project Overview
A structured relational SQLite database project built as part of the SQL & Database Management Systems virtual internship. It tracks library members, books, and issue/return loan transactions while supporting analytical queries on borrowing patterns and category popularity.

## 2. Database Schema & Normalization (3NF)
- **members (`member_id`, `full_name`, `email`, `joined_date`):** Stores unique member profiles with `PRIMARY KEY` and `UNIQUE` email constraint.
- **books (`book_id`, `title`, `author`, `category`, `total_copies`):** Stores catalog records with `CHECK (total_copies >= 0)`.
- **loans (`loan_id`, `member_id`, `book_id`, `issue_date`, `return_date`, `status`):** Tracks lending transactions using `FOREIGN KEY` constraints referencing `members` and `books`, with `CHECK (status IN ('Issued', 'Returned'))`.
- **Indexes:** Created on `loans(member_id)`, `loans(book_id)`, and `loans(status)` to optimize join and filter performance.

## 3. Key SQL Concepts & Queries Implemented
- **Multi-Table `JOIN`:** Listing currently issued books along with member names, book titles, categories, and issue dates.
- **`LEFT JOIN` + `GROUP BY` + `COUNT()`:** Calculating total loans per member and borrow counts per book without dropping records with zero loans.
- **`HAVING` Clause:** Filtering active borrowers who have taken 2 or more loans.
- **Category Aggregation (`SUM` & `COUNT`):** Summarizing total library copies and loan transactions by book category.
- **Transactional `UPDATE` Flow:** Marking an issued loan (`loan_id = 2`) as `Returned` with `return_date = '2026-11-19'` and verifying state change.

## 4. Viva / Evaluation Talking Points (MCA)
- **Why 3NF / Separate `loans` Table:** Separates entity attributes from transaction history to prevent data redundancy and update anomalies.
- **Why `LEFT JOIN` instead of `INNER JOIN` for counts:** Ensures books or members with zero loans still appear with `0` count in reports.
- **Why Indexes were added:** Speeds up foreign key lookups (`member_id`, `book_id`) and status filtering (`'Issued'` / `'Returned'`).