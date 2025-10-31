package services

import (
	"context"
	"database/sql"
	"fmt"
	"strings"

	"aihelper/internal/models"
	"aihelper/internal/ollama"
)

type RoleplayService struct {
	db      *sql.DB
	ollama  *ollama.Client
	charSvc *CharacterService
}

func NewRoleplayService(db *sql.DB, client *ollama.Client, charSvc *CharacterService) *RoleplayService {
	return &RoleplayService{db: db, ollama: client, charSvc: charSvc}
}

func (s *RoleplayService) CreateSession(ctx context.Context, session *models.RoleplaySession) error {
	result, err := s.db.ExecContext(ctx, `INSERT INTO sessions (character_id, setting, user_goals) VALUES (?, ?, ?)`,
		session.CharacterID, session.Setting, session.UserGoals)
	if err != nil {
		return err
	}
	session.ID, _ = result.LastInsertId()
	_, err = s.db.ExecContext(ctx, `INSERT INTO character_state (session_id, mood, memory, notes) VALUES (?, ?, ?, ?)`,
		session.ID, "neutral", "", "")
	return err
}

func (s *RoleplayService) ListSessions(ctx context.Context) ([]models.RoleplaySession, error) {
	rows, err := s.db.QueryContext(ctx, `SELECT id, character_id, setting, user_goals, start_time FROM sessions ORDER BY start_time DESC`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var sessions []models.RoleplaySession
	for rows.Next() {
		var sess models.RoleplaySession
		if err := rows.Scan(&sess.ID, &sess.CharacterID, &sess.Setting, &sess.UserGoals, &sess.StartTime); err != nil {
			return nil, err
		}
		sessions = append(sessions, sess)
	}
	return sessions, rows.Err()
}

func (s *RoleplayService) GetDialogue(ctx context.Context, sessionID int64) ([]models.Dialogue, error) {
	rows, err := s.db.QueryContext(ctx, `SELECT id, session_id, speaker, message, edited, timestamp FROM dialogue WHERE session_id = ? ORDER BY timestamp`, sessionID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var messages []models.Dialogue
	for rows.Next() {
		var d models.Dialogue
		if err := rows.Scan(&d.ID, &d.SessionID, &d.Speaker, &d.Message, &d.Edited, &d.Timestamp); err != nil {
			return nil, err
		}
		messages = append(messages, d)
	}
	return messages, rows.Err()
}

func (s *RoleplayService) SaveDialogue(ctx context.Context, dialogue *models.Dialogue) error {
	result, err := s.db.ExecContext(ctx, `INSERT INTO dialogue (session_id, speaker, message, edited) VALUES (?, ?, ?, ?)`,
		dialogue.SessionID, dialogue.Speaker, dialogue.Message, dialogue.Edited)
	if err != nil {
		return err
	}
	dialogue.ID, _ = result.LastInsertId()
	return nil
}

func (s *RoleplayService) UpdateDialogue(ctx context.Context, id int64, newMessage string) error {
	_, err := s.db.ExecContext(ctx, `UPDATE dialogue SET message = ?, edited = 1 WHERE id = ?`, newMessage, id)
	return err
}

func (s *RoleplayService) GetCharacterState(ctx context.Context, sessionID int64) (*models.CharacterState, error) {
	var state models.CharacterState
	err := s.db.QueryRowContext(ctx, `SELECT session_id, mood, memory, notes FROM character_state WHERE session_id = ?`, sessionID).
		Scan(&state.SessionID, &state.Mood, &state.Memory, &state.Notes)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}
	return &state, nil
}

func (s *RoleplayService) UpdateCharacterState(ctx context.Context, state *models.CharacterState) error {
	_, err := s.db.ExecContext(ctx, `UPDATE character_state SET mood = ?, memory = ?, notes = ? WHERE session_id = ?`,
		state.Mood, state.Memory, state.Notes, state.SessionID)
	return err
}

func (s *RoleplayService) GenerateResponse(ctx context.Context, sessionID int64, userMessage string) (string, error) {
	var characterID int64
	var setting string
	err := s.db.QueryRowContext(ctx, `SELECT character_id, setting FROM sessions WHERE id = ?`, sessionID).Scan(&characterID, &setting)
	if err != nil {
		return "", err
	}

	character, err := s.charSvc.GetCharacter(ctx, characterID)
	if err != nil {
		return "", err
	}
	if character == nil {
		return "", fmt.Errorf("character not found")
	}

	state, err := s.GetCharacterState(ctx, sessionID)
	if err != nil {
		return "", err
	}

	dialogue, err := s.GetDialogue(ctx, sessionID)
	if err != nil {
		return "", err
	}
	history := ""
	for _, d := range dialogue {
		history += fmt.Sprintf("%s: %s\n", d.Speaker, d.Message)
	}

	systemPrompt := fmt.Sprintf(`Ты — персонаж в ролевой игре.
Имя: %s
Возраст: %d
Пол: %s
Роль: %s
Черты: %s
Голос и стиль: %s
Цели: %s
Текущее настроение: %s
Важные воспоминания: %s
Контекст: %s
Диалог:
%s
Ответь как персонаж, не утрачивая характер, голос и цели.`,
		character.Name, character.Age, character.Gender, character.Description, character.Traits, character.Voice,
		character.Goals, state.Mood, state.Memory, setting, history)

	resp, err := s.ollama.Chat(ctx, systemPrompt, userMessage)
	if err != nil {
		return "", err
	}

	memory := state.Memory
	if len(strings.TrimSpace(userMessage)) > 50 {
		memory += "\n" + strings.TrimSpace(userMessage[:50]) + "..."
	}
	state.Memory = memory

	_ = s.UpdateCharacterState(ctx, state)
	return resp, nil
}
