package services

import (
	"context"
	"database/sql"

	"aihelper/internal/models"
)

type HistoryService struct {
	db *sql.DB
}

func NewHistoryService(db *sql.DB) *HistoryService {
	return &HistoryService{db: db}
}

func (s *HistoryService) SaveEntry(ctx context.Context, userText, resultText, styleApplied string, sessionID int64) error {
	_, err := s.db.ExecContext(ctx, `INSERT INTO chat_history (user_text, result_text, style_applied, session_id) VALUES (?, ?, ?, ?)`,
		userText, resultText, styleApplied, sessionID)
	return err
}

func (s *HistoryService) ListHistory(ctx context.Context, limit int) ([]models.ChatHistory, error) {
	rows, err := s.db.QueryContext(ctx, `SELECT id, time, user_text, result_text, style_applied, session_id FROM chat_history ORDER BY time DESC LIMIT ?`, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var history []models.ChatHistory
	for rows.Next() {
		var h models.ChatHistory
		if err := rows.Scan(&h.ID, &h.Time, &h.UserText, &h.ResultText, &h.StyleApplied, &h.SessionID); err != nil {
			return nil, err
		}
		history = append(history, h)
	}
	return history, rows.Err()
}
