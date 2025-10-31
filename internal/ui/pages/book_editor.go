package pages

import (
	"context"

	"aihelper/internal/services"
	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
)

func NewBookEditor(ctx context.Context, svc *services.BookService) fyne.CanvasObject {
	books, _ := svc.ListBooks(ctx)

	list := widget.NewList(
		func() int { return len(books) },
		func() fyne.CanvasObject { return widget.NewLabel("") },
		func(id widget.ListItemID, item fyne.CanvasObject) {
			item.(*widget.Label).SetText(books[id].Title)
		},
	)

	addButton := widget.NewButton("+ Создать книгу", func() {
		fyne.CurrentApp().SendNotification(&fyne.Notification{Title: "Редактор книг", Content: "Функция в разработке"})
	})

	return container.NewBorder(
		container.NewVBox(widget.NewLabelWithStyle("Редактор книг", fyne.TextAlignLeading, fyne.TextStyle{Bold: true}), widget.NewSeparator(), addButton),
		nil,
		list,
		nil,
		widget.NewLabel("Выберите книгу или создайте новую"),
	)
}
