package pages

import (
	"context"

	"aihelper/internal/models"
	"aihelper/internal/services"
	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/widget"
)

func NewStyleManager(ctx context.Context, styleService *services.StyleService) fyne.CanvasObject {
	styles, _ := styleService.ListStyles(ctx)

	list := widget.NewList(
		func() int { return len(styles) },
		func() fyne.CanvasObject { return widget.NewLabel("") },
		func(id widget.ListItemID, item fyne.CanvasObject) {
			label := item.(*widget.Label)
			label.SetText(styles[id].Name)
		},
	)

	detailArea := container.NewVBox()

	list.OnSelected = func(id widget.ListItemID) {
		style := &styles[id]
		showStyleDetails(ctx, style, styleService, detailArea, list, &styles)
	}

	addButton := widget.NewButton("+ Создать стиль", func() {
		newStyle := &models.Style{}
		showStyleForm(ctx, newStyle, styleService, func() {
			styles, _ = styleService.ListStyles(ctx)
			list.Refresh()
		})
	})

	return container.NewBorder(
		container.NewVBox(widget.NewLabelWithStyle("Менеджер стилей", fyne.TextAlignLeading, fyne.TextStyle{Bold: true}), widget.NewSeparator(), addButton),
		nil,
		list,
		nil,
		detailArea,
	)
}

func showStyleDetails(ctx context.Context, style *models.Style, svc *services.StyleService, detailArea *fyne.Container, list *widget.List, styles *[]models.Style) {
	nameLabel := widget.NewLabel("Название: " + style.Name)
	descLabel := widget.NewLabel("Описание: " + style.Description)
	rulesLabel := widget.NewLabel("Правила (YAML): " + style.YAMLRules)

	editButton := widget.NewButton("Редактировать", func() {
		showStyleForm(ctx, style, svc, func() {
			*styles, _ = svc.ListStyles(ctx)
			list.Refresh()
			showStyleDetails(ctx, style, svc, detailArea, list, styles)
		})
	})

	deleteButton := widget.NewButton("Удалить", func() {
		dialog.ShowConfirm("Удалить стиль?", "Вы уверены, что хотите удалить этот стиль?", func(confirm bool) {
			if confirm {
				_ = svc.DeleteStyle(ctx, style.ID)
				*styles, _ = svc.ListStyles(ctx)
				list.Refresh()
				detailArea.Objects = nil
			}
		}, currentWindow())
	})

	detailArea.Objects = []fyne.CanvasObject{
		nameLabel,
		descLabel,
		rulesLabel,
		container.NewHBox(editButton, deleteButton),
	}
	detailArea.Refresh()
}

func showStyleForm(ctx context.Context, style *models.Style, svc *services.StyleService, onSave func()) {
	nameEntry := widget.NewEntry()
	nameEntry.SetText(style.Name)
	nameEntry.SetPlaceHolder("Название стиля")

	descEntry := widget.NewEntry()
	descEntry.SetText(style.Description)
	descEntry.SetPlaceHolder("Описание")

	rulesEntry := widget.NewMultiLineEntry()
	rulesEntry.SetText(style.YAMLRules)
	rulesEntry.SetPlaceHolder("YAML правила (например: tone: formal, vocabulary: medieval)")

	activeCheck := widget.NewCheck("Активен", nil)
	activeCheck.Checked = style.Active

	form := widget.NewForm(
		widget.NewFormItem("Название", nameEntry),
		widget.NewFormItem("Описание", descEntry),
		widget.NewFormItem("Правила (YAML)", rulesEntry),
		widget.NewFormItem("Статус", activeCheck),
	)

	d := dialog.NewCustomConfirm("Редактирование стиля", "Сохранить", "Отмена", form, func(save bool) {
		if save {
			style.Name = nameEntry.Text
			style.Description = descEntry.Text
			style.YAMLRules = rulesEntry.Text
			style.Active = activeCheck.Checked
			_ = svc.SaveStyle(ctx, style)
			if onSave != nil {
				onSave()
			}
		}
	}, currentWindow())
	d.Resize(fyne.NewSize(600, 400))
	d.Show()
}
