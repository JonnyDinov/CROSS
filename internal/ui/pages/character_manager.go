package pages

import (
	"context"
	"strconv"

	"aihelper/internal/models"
	"aihelper/internal/services"
	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/widget"
)

func NewCharacterManager(ctx context.Context, svc *services.CharacterService) fyne.CanvasObject {
	characters, _ := svc.ListCharacters(ctx)

	list := widget.NewList(
		func() int { return len(characters) },
		func() fyne.CanvasObject { return widget.NewLabel("") },
		func(id widget.ListItemID, item fyne.CanvasObject) {
			item.(*widget.Label).SetText(characters[id].Name)
		},
	)

	detail := container.NewVBox()

	refresh := func() {
		characters, _ = svc.ListCharacters(ctx)
		list.Refresh()
	}

	list.OnSelected = func(id widget.ListItemID) {
		if id < 0 || id >= len(characters) {
			return
		}
		showCharacterDetail(ctx, &characters[id], svc, detail, refresh)
	}

	addButton := widget.NewButton("+ Создать персонажа", func() {
		char := &models.Character{}
		showCharacterForm(ctx, char, svc, refresh)
	})

	title := widget.NewLabelWithStyle("База персонажей", fyne.TextAlignLeading, fyne.TextStyle{Bold: true})

	return container.NewBorder(
		container.NewVBox(title, widget.NewSeparator(), addButton),
		nil,
		list,
		nil,
		detail,
	)
}

func showCharacterDetail(ctx context.Context, character *models.Character, svc *services.CharacterService, detail *fyne.Container, onUpdate func()) {
	labels := []*widget.Label{
		widget.NewLabel("Имя: " + character.Name),
		widget.NewLabel("Возраст: " + strconv.Itoa(character.Age)),
		widget.NewLabel("Пол: " + character.Gender),
		widget.NewLabel("Описание: " + character.Description),
		widget.NewLabel("Голос: " + character.Voice),
		widget.NewLabel("Цели: " + character.Goals),
		widget.NewLabel("Черты: " + character.Traits),
		widget.NewLabel("Био: " + character.Bio),
	}

	editButton := widget.NewButton("Редактировать", func() {
		showCharacterForm(ctx, character, svc, func() {
			onUpdate()
			showCharacterDetail(ctx, character, svc, detail, onUpdate)
		})
	})

	deleteButton := widget.NewButton("Удалить", func() {
		dialog.ShowConfirm("Удалить персонажа?", "Персонаж и связанные данные будут удалены", func(yes bool) {
			if yes {
				_ = svc.DeleteCharacter(ctx, character.ID)
				onUpdate()
				detail.Objects = nil
			}
		}, currentWindow())
	})

	objects := make([]fyne.CanvasObject, 0, len(labels)+1)
	for _, label := range labels {
		objects = append(objects, label)
	}
	objects = append(objects, container.NewHBox(editButton, deleteButton))

	detail.Objects = objects
	detail.Refresh()
}

func showCharacterForm(ctx context.Context, character *models.Character, svc *services.CharacterService, onSave func()) {
	name := widget.NewEntry()
	name.SetText(character.Name)

	age := widget.NewEntry()
	if character.Age != 0 {
		age.SetText(strconv.Itoa(character.Age))
	}

	gender := widget.NewEntry()
	gender.SetText(character.Gender)

	desc := widget.NewMultiLineEntry()
	desc.SetText(character.Description)

	voice := widget.NewEntry()
	voice.SetText(character.Voice)

	goals := widget.NewMultiLineEntry()
	goals.SetText(character.Goals)

	traits := widget.NewMultiLineEntry()
	traits.SetText(character.Traits)

	bio := widget.NewMultiLineEntry()
	bio.SetText(character.Bio)

	form := widget.NewForm(
		widget.NewFormItem("Имя", name),
		widget.NewFormItem("Возраст", age),
		widget.NewFormItem("Пол", gender),
		widget.NewFormItem("Описание", desc),
		widget.NewFormItem("Голос", voice),
		widget.NewFormItem("Цели", goals),
		widget.NewFormItem("Черты", traits),
		widget.NewFormItem("Биография", bio),
	)

	dlg := dialog.NewCustomConfirm("Персонаж", "Сохранить", "Отмена", form, func(save bool) {
		if !save {
			return
		}

		character.Name = name.Text
		character.Gender = gender.Text
		character.Description = desc.Text
		character.Voice = voice.Text
		character.Goals = goals.Text
		character.Traits = traits.Text
		character.Bio = bio.Text

		if age.Text != "" {
			if v, err := strconv.Atoi(age.Text); err == nil {
				character.Age = v
			}
		}

		_ = svc.SaveCharacter(ctx, character)
		if onSave != nil {
			onSave()
		}
	}, currentWindow())
	dlg.Resize(fyne.NewSize(600, 500))
	dlg.Show()
}
