package services

import (
	"context"
	"database/sql"
	"errors"
	"fmt"

	"aihelper/internal/models"
	"aihelper/internal/ollama"
)

type StyleService struct {
	db      *sql.DB
	client  *ollama.Client
	History *HistoryService
}

func NewStyleService(db *sql.DB, client *ollama.Client, history *HistoryService) *StyleService {
	return &StyleService{db: db, client: client, History: history}
}

func (s *StyleService) ListStyles(ctx context.Context) ([]models.Style, error) {
	rows, err := s.db.QueryContext(ctx, `SELECT id, name, description, yaml_rules, active, created_at FROM styles ORDER BY name`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var styles []models.Style
	for rows.Next() {
		var style models.Style
		if err := rows.Scan(&style.ID, &style.Name, &style.Description, &style.YAMLRules, &style.Active, &style.CreatedAt); err != nil {
			return nil, err
		}
		styles = append(styles, style)
	}
	return styles, rows.Err()
}

func (s *StyleService) GetStyle(ctx context.Context, id int64) (*models.Style, error) {
	var style models.Style
	err := s.db.QueryRowContext(ctx, `SELECT id, name, description, yaml_rules, active, created_at FROM styles WHERE id = ?`, id).
		Scan(&style.ID, &style.Name, &style.Description, &style.YAMLRules, &style.Active, &style.CreatedAt)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, nil
		}
		return nil, err
	}
	return &style, nil
}

func (s *StyleService) SaveStyle(ctx context.Context, style *models.Style) error {
	if style.ID == 0 {
		result, err := s.db.ExecContext(ctx, `INSERT INTO styles (name, description, yaml_rules, active) VALUES (?, ?, ?, ?)`,
			style.Name, style.Description, style.YAMLRules, style.Active)
		if err != nil {
			return err
		}
		style.ID, _ = result.LastInsertId()
		return nil
	}
	_, err := s.db.ExecContext(ctx, `UPDATE styles SET name = ?, description = ?, yaml_rules = ?, active = ? WHERE id = ?`,
		style.Name, style.Description, style.YAMLRules, style.Active, style.ID)
	return err
}

func (s *StyleService) DeleteStyle(ctx context.Context, id int64) error {
	_, err := s.db.ExecContext(ctx, `DELETE FROM styles WHERE id = ?`, id)
	return err
}

type RewriteOptions struct {
	StyleID    int64
	StyleName  string
	Age        string
	Additional string
}

func (s *StyleService) RewriteText(ctx context.Context, original string, opts RewriteOptions) (string, error) {
	style, err := s.GetStyle(ctx, opts.StyleID)
	if err != nil {
		return "", err
	}
	if style == nil {
		style = &models.Style{Name: opts.StyleName}
	}

	prompt := fmt.Sprintf("Ты — редактор текста. Перепиши данное сообщение в стиле \"%s\".\nВозраст автора: %s.\nТребования: %s\nКонтекст: %s\nСохрани смысл, имена собственные и структуру.\nТекст:\n%s",
		style.Name, opts.Age, style.YAMLRules, opts.Additional, original)

	resp, err := s.client.Chat(ctx, "Ты — профессиональный литературный редактор.", prompt)
	if err != nil {
		return "", err
	}

	if s.History != nil {
		_ = s.History.SaveEntry(ctx, original, resp, style.Name, 0)
	}
	return resp, nil
}
