package services

import (
	"context"
	"database/sql"
	"fmt"

	"aihelper/internal/models"
	"aihelper/internal/ollama"
)

type QuestService struct {
	db     *sql.DB
	ollama *ollama.Client
}

func NewQuestService(db *sql.DB, client *ollama.Client) *QuestService {
	return &QuestService{db: db, ollama: client}
}

func (s *QuestService) CreateQuest(ctx context.Context, quest *models.Quest, steps []models.QuestStep) error {
	return transact(ctx, s.db, func(tx *sql.Tx) error {
		result, err := tx.ExecContext(ctx, `INSERT INTO quests (title, description, genre, characters, difficulty, rewards, json) VALUES (?, ?, ?, ?, ?, ?, ?)`,
			quest.Title, quest.Description, quest.Genre, quest.Characters, quest.Difficulty, quest.Rewards, quest.JSON)
		if err != nil {
			return err
		}
		quest.ID, _ = result.LastInsertId()
		for _, step := range steps {
			_, err := tx.ExecContext(ctx, `INSERT INTO quest_steps (quest_id, step_number, content) VALUES (?, ?, ?)`, quest.ID, step.StepNumber, step.Content)
			if err != nil {
				return err
			}
		}
		return nil
	})
}

func (s *QuestService) ListQuests(ctx context.Context) ([]models.Quest, error) {
	rows, err := s.db.QueryContext(ctx, `SELECT id, title, description, genre, characters, difficulty, rewards, json, created_at FROM quests ORDER BY created_at DESC`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var quests []models.Quest
	for rows.Next() {
		var q models.Quest
		if err := rows.Scan(&q.ID, &q.Title, &q.Description, &q.Genre, &q.Characters, &q.Difficulty, &q.Rewards, &q.JSON, &q.CreatedAt); err != nil {
			return nil, err
		}
		quests = append(quests, q)
	}
	return quests, rows.Err()
}

func (s *QuestService) GenerateQuest(ctx context.Context, style, genre, difficulty, synopsis string, characters []models.Character) (string, error) {
	characterList := ""
	for i, character := range characters {
		if i > 0 {
			characterList += ", "
		}
		characterList += fmt.Sprintf("%s (%s)", character.Name, character.Traits)
	}

	systemPrompt := "Ты — опытный сценарист и геймдизайнер, создающий увлекательные квесты."
	userPrompt := fmt.Sprintf(`Сгенерируй квест в стиле "%s".
Жанр: %s.
Сложность: %s.
Персонажи: %s
Синопсис: %s
Формат Markdown:
- Заголовок
- Краткая суть
- Персонажи (имя, роль, характер)
- Цели игрока поэтапно
- Диалоги
- Возможные варианты/развязки
- Награды`, style, genre, difficulty, characterList, synopsis)

	return s.ollama.Chat(ctx, systemPrompt, userPrompt)
}
