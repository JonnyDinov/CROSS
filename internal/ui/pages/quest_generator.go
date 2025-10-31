package pages

import (
	"context"

	"aihelper/internal/models"
	"aihelper/internal/services"
	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
)

func NewQuestGenerator(ctx context.Context, questSvc *services.QuestService, charSvc *services.CharacterService) fyne.CanvasObject {
	styleEntry := widget.NewEntry()
	styleEntry.SetPlaceHolder("Например: средневековый, киберпанк")

	genreEntry := widget.NewEntry()
	genreEntry.SetPlaceHolder("Например: фэнтези, научная фантастика")

	difficultySelect := widget.NewSelect([]string{"Легкий", "Средний", "Сложный", "Эксперт"}, nil)
	difficultySelect.PlaceHolder = "Выберите сложность"

	synopsisEntry := widget.NewMultiLineEntry()
	synopsisEntry.SetPlaceHolder("Краткое описание сюжета квеста...")

	characters, _ := charSvc.ListCharacters(ctx)
	charNames := make([]string, len(characters))
	for i, c := range characters {
		charNames[i] = c.Name
	}

	charCheck := widget.NewCheckGroup(charNames, nil)

	resultEntry := widget.NewMultiLineEntry()
	resultEntry.Disable()

	generateButton := widget.NewButton("Сгенерировать квест", func() {
		selectedChars := []models.Character{}
		for _, name := range charCheck.Selected {
			for _, c := range characters {
				if c.Name == name {
					selectedChars = append(selectedChars, c)
					break
				}
			}
		}

		resultEntry.SetText("Генерируем квест... это может занять несколько секунд")
		result, err := questSvc.GenerateQuest(ctx, styleEntry.Text, genreEntry.Text, difficultySelect.Selected, synopsisEntry.Text, selectedChars)
		if err != nil {
			resultEntry.SetText("Ошибка: " + err.Error())
			return
		}

		resultEntry.SetText(result)
		fyne.CurrentApp().SendNotification(&fyne.Notification{Title: "Генератор квестов", Content: "Квест готов"})
	})

	return container.NewVBox(
		widget.NewLabelWithStyle("Генератор квестов", fyne.TextAlignLeading, fyne.TextStyle{Bold: true}),
		widget.NewSeparator(),
		widget.NewForm(
			widget.NewFormItem("Стиль", styleEntry),
			widget.NewFormItem("Жанр", genreEntry),
			widget.NewFormItem("Сложность", difficultySelect),
		),
		widget.NewLabel("Синопсис"),
		synopsisEntry,
		widget.NewLabel("Персонажи"),
		charCheck,
		generateButton,
		widget.NewSeparator(),
		widget.NewLabel("Результат"),
		resultEntry,
	)
}
