package storage

import (
	"database/sql"
	"fmt"
	"os"
	"path/filepath"
	"time"

	_ "modernc.org/sqlite"
)

type Manager struct {
	Characters *sql.DB
	Quests     *sql.DB
	Books      *sql.DB
	Styles     *sql.DB
	Roleplay   *sql.DB
	History    *sql.DB
	baseDir    string
}

func NewManager(baseDir string) (*Manager, error) {
	if err := os.MkdirAll(baseDir, 0o755); err != nil {
		return nil, fmt.Errorf("create database dir: %w", err)
	}

	manager := &Manager{baseDir: baseDir}

	openDB := func(name string) (*sql.DB, error) {
		dbPath := filepath.Join(baseDir, fmt.Sprintf("%s.db", name))
		db, err := sql.Open("sqlite", dbPath)
		if err != nil {
			return nil, fmt.Errorf("open %s: %w", name, err)
		}
		if _, err := db.Exec("PRAGMA foreign_keys = ON; PRAGMA busy_timeout = 5000;"); err != nil {
			return nil, fmt.Errorf("configure %s: %w", name, err)
		}
		return db, nil
	}

	var err error
	if manager.Characters, err = openDB("characters"); err != nil {
		return nil, err
	}
	if manager.Quests, err = openDB("quests"); err != nil {
		return nil, err
	}
	if manager.Books, err = openDB("books"); err != nil {
		return nil, err
	}
	if manager.Styles, err = openDB("styles"); err != nil {
		return nil, err
	}
	if manager.Roleplay, err = openDB("roleplay_sessions"); err != nil {
		return nil, err
	}
	if manager.History, err = openDB("history"); err != nil {
		return nil, err
	}

	if err := manager.createSchemas(); err != nil {
		return nil, err
	}

	return manager, nil
}

func (m *Manager) Close() error {
	dbs := []*sql.DB{m.Characters, m.Quests, m.Books, m.Styles, m.Roleplay, m.History}
	for _, db := range dbs {
		if db == nil {
			continue
		}
		if err := db.Close(); err != nil {
			return err
		}
	}
	return nil
}

func (m *Manager) createSchemas() error {
	creators := []func() error{
		m.initCharacters,
		m.initQuests,
		m.initBooks,
		m.initStyles,
		m.initRoleplay,
		m.initHistory,
	}
	for _, creator := range creators {
		if err := creator(); err != nil {
			return err
		}
	}
	return nil
}

func (m *Manager) initCharacters() error {
	statements := []string{
		`CREATE TABLE IF NOT EXISTS characters (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL,
			age INTEGER,
			gender TEXT,
			description TEXT,
			voice TEXT,
			goals TEXT,
			traits TEXT,
			bio TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);`,
		`CREATE TABLE IF NOT EXISTS relationships (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			character_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
			target_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
			relation TEXT,
			notes TEXT
		);`,
	}
	for _, stmt := range statements {
		if _, err := m.Characters.Exec(stmt); err != nil {
			return fmt.Errorf("init characters: %w", err)
		}
	}
	return nil
}

func (m *Manager) initQuests() error {
	statements := []string{
		`CREATE TABLE IF NOT EXISTS quests (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			title TEXT NOT NULL,
			description TEXT,
			genre TEXT,
			characters TEXT,
			difficulty TEXT,
			rewards TEXT,
			json TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);`,
		`CREATE TABLE IF NOT EXISTS quest_steps (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			quest_id INTEGER NOT NULL REFERENCES quests(id) ON DELETE CASCADE,
			step_number INTEGER NOT NULL,
			content TEXT
		);`,
	}
	for _, stmt := range statements {
		if _, err := m.Quests.Exec(stmt); err != nil {
			return fmt.Errorf("init quests: %w", err)
		}
	}
	return nil
}

func (m *Manager) initBooks() error {
	statements := []string{
		`CREATE TABLE IF NOT EXISTS books (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			title TEXT NOT NULL,
			author TEXT,
			chars_per_page INTEGER DEFAULT 1000,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);`,
		`CREATE TABLE IF NOT EXISTS pages (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
			page_number INTEGER NOT NULL,
			content TEXT
		);`,
	}
	for _, stmt := range statements {
		if _, err := m.Books.Exec(stmt); err != nil {
			return fmt.Errorf("init books: %w", err)
		}
	}
	return nil
}

func (m *Manager) initStyles() error {
	stmt := `CREATE TABLE IF NOT EXISTS styles (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL,
		description TEXT,
		yaml_rules TEXT,
		active INTEGER DEFAULT 1,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);`
	if _, err := m.Styles.Exec(stmt); err != nil {
		return fmt.Errorf("init styles: %w", err)
	}
	return nil
}

func (m *Manager) initRoleplay() error {
	statements := []string{
		`CREATE TABLE IF NOT EXISTS sessions (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			character_id INTEGER REFERENCES characters(id),
			setting TEXT,
			user_goals TEXT,
			start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);`,
		`CREATE TABLE IF NOT EXISTS dialogue (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
			speaker TEXT,
			message TEXT,
			edited INTEGER DEFAULT 0,
			timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);`,
		`CREATE TABLE IF NOT EXISTS character_state (
			session_id INTEGER PRIMARY KEY REFERENCES sessions(id) ON DELETE CASCADE,
			mood TEXT,
			memory TEXT,
			notes TEXT
		);`,
	}
	for _, stmt := range statements {
		if _, err := m.Roleplay.Exec(stmt); err != nil {
			return fmt.Errorf("init roleplay: %w", err)
		}
	}
	return nil
}

func (m *Manager) initHistory() error {
	stmt := `CREATE TABLE IF NOT EXISTS chat_history (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		user_text TEXT,
		result_text TEXT,
		style_applied TEXT,
		session_id INTEGER
	);`
	if _, err := m.History.Exec(stmt); err != nil {
		return fmt.Errorf("init history: %w", err)
	}
	return nil
}

func (m *Manager) VacuumAll() {
	dbs := []*sql.DB{m.Characters, m.Quests, m.Books, m.Styles, m.Roleplay, m.History}
	for _, db := range dbs {
		if db == nil {
			continue
		}
		_, _ = db.Exec("VACUUM;")
	}
}

func (m *Manager) LastVacuum() time.Time {
	return time.Now()
}
