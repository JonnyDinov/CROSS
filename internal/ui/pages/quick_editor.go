package pages

import (
	"context"
	"strings"

	"aihelper/internal/services"
	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/widget"
)

func NewQuickEditor(ctx context.Context, styles *services.StyleService) fyne.CanvasObject {
	textEntry := widget.NewMultiLineEntry()
	textEntry.SetPlaceHolder("Вставьте текст для преобразования...")

	resultEntry := widget.NewMultiLineEntry()
	resultEntry.Disable()

	stylesCache, _ := styles.ListStyles(ctx)
	styleNames := make([]string, len(stylesCache))
	styleIDs := make([]int64, len(stylesCache))
	for i, style := range stylesCache {
		styleNames[i] = style.Name
		styleIDs[i] = style.ID
	}
	styleSelect := widget.NewSelect(styleNames, nil)
	styleSelect.PlaceHolder = "Выберите стиль"

	ageEntry := widget.NewEntry()
	ageEntry.SetPlaceHolder("Возраст автора")

	contextEntry := widget.NewEntry()
	contextEntry.SetPlaceHolder("Дополнительный контекст")

	applyButton := widget.NewButton("Переписать текст", func() {
		styleID := int64(0)
		styleName := strings.TrimSpace(styleSelect.Selected)
		for i, name := range styleNames {
			if name == styleName {
				styleID = styleIDs[i]
				break
			}
		}

		if styleName == "" {
			if w := currentWindow(); w != nil {
				dialog.ShowInformation("Стиль не выбран", "Выберите стиль или создайте новый в менеджере стилей.", w)
			}
			return
		}

		resultEntry.SetText("Переписываем... это может занять несколько секунд")

		opts := services.RewriteOptions{StyleID: styleID, StyleName: styleName, Age: ageEntry.Text, Additional: contextEntry.Text}
		res, err := styles.RewriteText(ctx, textEntry.Text, opts)
		if err != nil {
			if w := currentWindow(); w != nil {
				dialog.ShowError(err, w)
			}
			resultEntry.SetText("Ошибка: " + err.Error())
			return
		}

		resultEntry.SetText(res)
		fyne.CurrentApp().SendNotification(&fyne.Notification{Title: "Быстрый редактор", Content: "Готово"})
	})

	return container.NewVBox(
		widget.NewLabelWithStyle("Быстрый ИИ-редактор", fyne.TextAlignLeading, fyne.TextStyle{Bold: true}),
		widget.NewSeparator(),
		widget.NewForm(
			widget.NewFormItem("Стиль", styleSelect),
			widget.NewFormItem("Возраст", ageEntry),
			widget.NewFormItem("Контекст", contextEntry),
		),
		applyButton,
		widget.NewSeparator(),
		widget.NewLabel("Исходный текст"),
		textEntry,
		widget.NewLabel("Результат"),
		resultEntry,
	)
}
