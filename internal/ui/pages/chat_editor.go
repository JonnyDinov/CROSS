package pages

import (
	"context"

	"aihelper/internal/services"
	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
)

func NewChatEditor(ctx context.Context, history *services.HistoryService, styles *services.StyleService) fyne.CanvasObject {
	chatInput := widget.NewMultiLineEntry()
	chatInput.SetPlaceHolder("Введите сообщение или текст...")

	result := widget.NewMultiLineEntry()
	result.Disable()

	historyList := widget.NewList(
		func() int {
			records, _ := history.ListHistory(ctx, 50)
			return len(records)
		},
		func() fyne.CanvasObject { return widget.NewLabel("") },
		func(id widget.ListItemID, item fyne.CanvasObject) {
			records, _ := history.ListHistory(ctx, 50)
			item.(*widget.Label).SetText(records[id].UserText)
		},
	)

	rewrite := widget.NewButton("Переписать стилем...", func() {
		fyne.CurrentApp().SendNotification(&fyne.Notification{Title: "Чат-редактор", Content: "Выберите стиль в быстром редакторе"})
	})

	send := widget.NewButton("Отправить в историю", func() {
		if chatInput.Text == "" {
			return
		}
		_ = history.SaveEntry(ctx, chatInput.Text, result.Text, "", 0)
		historyList.Refresh()
	})

	return container.NewBorder(
		widget.NewLabelWithStyle("Чат-редактор", fyne.TextAlignLeading, fyne.TextStyle{Bold: true}),
		nil,
		container.NewVBox(widget.NewLabel("История"), historyList),
		nil,
		container.NewVBox(chatInput, container.NewHBox(rewrite, send), widget.NewLabel("Результат"), result),
	)
}
