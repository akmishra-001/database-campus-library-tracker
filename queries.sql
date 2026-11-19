-- 1. Currently Issued Books with Member & Book Details (Multi-table JOIN)
SELECT 
    l.loan_id,
    m.full_name AS member_name,
    b.title AS book_title,
    b.category,
    l.issue_date,
    l.status
FROM loans l
JOIN members m ON l.member_id = m.member_id
JOIN books b ON l.book_id = b.book_id
WHERE l.status = 'Issued'
ORDER BY l.issue_date ASC;

-- 2. Member-wise Total Loans Count (GROUP BY + COUNT)
SELECT 
    m.member_id,
    m.full_name,
    COUNT(l.loan_id) AS total_loans
FROM members m
LEFT JOIN loans l ON m.member_id = l.member_id
GROUP BY m.member_id, m.full_name
ORDER BY total_loans DESC, m.member_id ASC;

-- 3. Most Borrowed Books Ranking (JOIN + GROUP BY + COUNT + ORDER BY)
SELECT 
    b.book_id,
    b.title,
    b.author,
    COUNT(l.loan_id) AS borrow_count
FROM books b
LEFT JOIN loans l ON b.book_id = l.book_id
GROUP BY b.book_id, b.title, b.author
ORDER BY borrow_count DESC, b.book_id ASC;

-- 4. Active Borrowers Having 2 or More Loans (GROUP BY + HAVING)
SELECT 
    m.full_name,
    COUNT(l.loan_id) AS loan_count
FROM members m
JOIN loans l ON m.member_id = l.member_id
GROUP BY m.member_id, m.full_name
HAVING COUNT(l.loan_id) >= 2
ORDER BY loan_count DESC, m.full_name ASC;

-- 5. Category-wise Loan Summary & Available Copies Calculation
SELECT 
    b.category,
    SUM(b.total_copies) AS total_library_copies,
    COUNT(l.loan_id) AS total_loan_transactions
FROM books b
LEFT JOIN loans l ON b.book_id = l.book_id
GROUP BY b.category
ORDER BY total_loan_transactions DESC, b.category ASC;