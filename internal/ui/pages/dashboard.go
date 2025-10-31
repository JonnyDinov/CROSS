package pages

import (
	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/theme"
	"fyne.io/fyne/v2/widget"
)

func NewDashboard() fyne.CanvasObject {
	title := canvas.NewText("Главное меню", theme.ForegroundColor())
	title.TextSize = 32
	title.TextStyle = fyne.TextStyle{Bold: true}

	subtitle := canvas.NewText("AI Helper — офлайн‑редактор текста с ролевыми и писательскими функциями", theme.ForegroundColor())
	subtitle.TextSize = 16

	features := widget.NewLabel(`
🚀 Основные возможности:

• Alt+W - Быстрый редактор текста (преобразование по стилю)
• Alt+F - Главное меню (доступ ко всем функциям)

• Менеджер стилей - настройка и управление стилями текста
• База персонажей - создание и хранение персонажей для историй
• Генератор квестов - автоматическое создание квестов и сюжетов
• Редактор книг - работа с текстами книг и главами
• Чат-редактор - работа с длинными текстами через чат
• Ролевая игра - интерактивное общение с ИИ-персонажами

Все данные хранятся локально в SQLite базах данных.
ИИ работает через Ollama (модель: deepseek-v3.1:671b-cloud)
	`)
	features.Wrapping = fyne.TextWrapWord

	helpCard := widget.NewCard("Информация", "", features)

	return container.NewVBox(
		title,
		subtitle,
		widget.NewSeparator(),
		helpCard,
	)
}
