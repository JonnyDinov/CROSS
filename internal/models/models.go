package models

import "time"

type Character struct {
	ID          int64     `db:"id"`
	Name        string    `db:"name"`
	Age         int       `db:"age"`
	Gender      string    `db:"gender"`
	Description string    `db:"description"`
	Voice       string    `db:"voice"`
	Goals       string    `db:"goals"`
	Traits      string    `db:"traits"`
	Bio         string    `db:"bio"`
	CreatedAt   time.Time `db:"created_at"`
}

type Relationship struct {
	ID          int64  `db:"id"`
	CharacterID int64  `db:"character_id"`
	TargetID    int64  `db:"target_id"`
	Relation    string `db:"relation"`
	Notes       string `db:"notes"`
}

type Quest struct {
	ID          int64     `db:"id"`
	Title       string    `db:"title"`
	Description string    `db:"description"`
	Genre       string    `db:"genre"`
	Characters  string    `db:"characters"`
	Difficulty  string    `db:"difficulty"`
	Rewards     string    `db:"rewards"`
	JSON        string    `db:"json"`
	CreatedAt   time.Time `db:"created_at"`
}

type QuestStep struct {
	ID         int64  `db:"id"`
	QuestID    int64  `db:"quest_id"`
	StepNumber int    `db:"step_number"`
	Content    string `db:"content"`
}

type Book struct {
	ID           int64     `db:"id"`
	Title        string    `db:"title"`
	Author       string    `db:"author"`
	CharsPerPage int       `db:"chars_per_page"`
	CreatedAt    time.Time `db:"created_at"`
}

type Page struct {
	ID         int64  `db:"id"`
	BookID     int64  `db:"book_id"`
	PageNumber int    `db:"page_number"`
	Content    string `db:"content"`
}

type Style struct {
	ID          int64     `db:"id"`
	Name        string    `db:"name"`
	Description string    `db:"description"`
	YAMLRules   string    `db:"yaml_rules"`
	Active      bool      `db:"active"`
	CreatedAt   time.Time `db:"created_at"`
}

type RoleplaySession struct {
	ID          int64     `db:"id"`
	CharacterID int64     `db:"character_id"`
	Setting     string    `db:"setting"`
	UserGoals   string    `db:"user_goals"`
	StartTime   time.Time `db:"start_time"`
}

type Dialogue struct {
	ID        int64     `db:"id"`
	SessionID int64     `db:"session_id"`
	Speaker   string    `db:"speaker"`
	Message   string    `db:"message"`
	Edited    bool      `db:"edited"`
	Timestamp time.Time `db:"timestamp"`
}

type CharacterState struct {
	SessionID int64  `db:"session_id"`
	Mood      string `db:"mood"`
	Memory    string `db:"memory"`
	Notes     string `db:"notes"`
}

type ChatHistory struct {
	ID           int64     `db:"id"`
	Time         time.Time `db:"time"`
	UserText     string    `db:"user_text"`
	ResultText   string    `db:"result_text"`
	StyleApplied string    `db:"style_applied"`
	SessionID    int64     `db:"session_id"`
}
