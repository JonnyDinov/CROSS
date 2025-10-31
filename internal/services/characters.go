package services

import (
	"context"
	"database/sql"
	"errors"

	"aihelper/internal/models"
)

type CharacterService struct {
	db *sql.DB
}

func NewCharacterService(db *sql.DB) *CharacterService {
	return &CharacterService{db: db}
}

func (s *CharacterService) ListCharacters(ctx context.Context) ([]models.Character, error) {
	rows, err := s.db.QueryContext(ctx, `SELECT id, name, age, gender, description, voice, goals, traits, bio, created_at FROM characters ORDER BY name`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var chars []models.Character
	for rows.Next() {
		var c models.Character
		if err := rows.Scan(&c.ID, &c.Name, &c.Age, &c.Gender, &c.Description, &c.Voice, &c.Goals, &c.Traits, &c.Bio, &c.CreatedAt); err != nil {
			return nil, err
		}
		chars = append(chars, c)
	}
	return chars, rows.Err()
}

func (s *CharacterService) GetCharacter(ctx context.Context, id int64) (*models.Character, error) {
	var c models.Character
	err := s.db.QueryRowContext(ctx, `SELECT id, name, age, gender, description, voice, goals, traits, bio, created_at FROM characters WHERE id = ?`, id).
		Scan(&c.ID, &c.Name, &c.Age, &c.Gender, &c.Description, &c.Voice, &c.Goals, &c.Traits, &c.Bio, &c.CreatedAt)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, nil
		}
		return nil, err
	}
	return &c, nil
}

func (s *CharacterService) SaveCharacter(ctx context.Context, c *models.Character) error {
	if c.ID == 0 {
		result, err := s.db.ExecContext(ctx, `INSERT INTO characters (name, age, gender, description, voice, goals, traits, bio) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
			c.Name, c.Age, c.Gender, c.Description, c.Voice, c.Goals, c.Traits, c.Bio)
		if err != nil {
			return err
		}
		c.ID, _ = result.LastInsertId()
		return nil
	}
	_, err := s.db.ExecContext(ctx, `UPDATE characters SET name = ?, age = ?, gender = ?, description = ?, voice = ?, goals = ?, traits = ?, bio = ? WHERE id = ?`,
		c.Name, c.Age, c.Gender, c.Description, c.Voice, c.Goals, c.Traits, c.Bio, c.ID)
	return err
}

func (s *CharacterService) DeleteCharacter(ctx context.Context, id int64) error {
	_, err := s.db.ExecContext(ctx, `DELETE FROM characters WHERE id = ?`, id)
	return err
}

func (s *CharacterService) ListRelationships(ctx context.Context, characterID int64) ([]models.Relationship, error) {
	rows, err := s.db.QueryContext(ctx, `SELECT id, character_id, target_id, relation, notes FROM relationships WHERE character_id = ?`, characterID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var rels []models.Relationship
	for rows.Next() {
		var r models.Relationship
		if err := rows.Scan(&r.ID, &r.CharacterID, &r.TargetID, &r.Relation, &r.Notes); err != nil {
			return nil, err
		}
		rels = append(rels, r)
	}
	return rels, rows.Err()
}
