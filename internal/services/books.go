package services

import (
	"context"
	"database/sql"

	"aihelper/internal/models"
)

type BookService struct {
	db *sql.DB
}

func NewBookService(db *sql.DB) *BookService {
	return &BookService{db: db}
}

func (s *BookService) CreateBook(ctx context.Context, book *models.Book) error {
	result, err := s.db.ExecContext(ctx, `INSERT INTO books (title, author, chars_per_page) VALUES (?, ?, ?)`, book.Title, book.Author, book.CharsPerPage)
	if err != nil {
		return err
	}
	book.ID, _ = result.LastInsertId()
	return nil
}

func (s *BookService) ListBooks(ctx context.Context) ([]models.Book, error) {
	rows, err := s.db.QueryContext(ctx, `SELECT id, title, author, chars_per_page, created_at FROM books ORDER BY created_at DESC`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var books []models.Book
	for rows.Next() {
		var b models.Book
		if err := rows.Scan(&b.ID, &b.Title, &b.Author, &b.CharsPerPage, &b.CreatedAt); err != nil {
			return nil, err
		}
		books = append(books, b)
	}
	return books, rows.Err()
}

func (s *BookService) GetPages(ctx context.Context, bookID int64) ([]models.Page, error) {
	rows, err := s.db.QueryContext(ctx, `SELECT id, book_id, page_number, content FROM pages WHERE book_id = ? ORDER BY page_number`, bookID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var pages []models.Page
	for rows.Next() {
		var p models.Page
		if err := rows.Scan(&p.ID, &p.BookID, &p.PageNumber, &p.Content); err != nil {
			return nil, err
		}
		pages = append(pages, p)
	}
	return pages, rows.Err()
}

func (s *BookService) SavePage(ctx context.Context, page *models.Page) error {
	if page.ID == 0 {
		result, err := s.db.ExecContext(ctx, `INSERT INTO pages (book_id, page_number, content) VALUES (?, ?, ?)`,
			page.BookID, page.PageNumber, page.Content)
		if err != nil {
			return err
		}
		page.ID, _ = result.LastInsertId()
		return nil
	}
	_, err := s.db.ExecContext(ctx, `UPDATE pages SET page_number = ?, content = ? WHERE id = ?`, page.PageNumber, page.Content, page.ID)
	return err
}
