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

func NewRoleplayEngine(ctx context.Context, roleplaySvc *services.RoleplayService, charSvc *services.CharacterService) fyne.CanvasObject {
	sessions, _ := roleplaySvc.ListSessions(ctx)

	list := widget.NewList(
		func() int { return len(sessions) },
		func() fyne.CanvasObject { return widget.NewLabel("") },
		func(id widget.ListItemID, item fyne.CanvasObject) {
			item.(*widget.Label).SetText("Сессия #" + strconv.FormatInt(sessions[id].ID, 10))
		},
	)

	chatArea := container.NewVBox()
	var currentSessionID int64 = 0

	refresh := func() {
		sessions, _ = roleplaySvc.ListSessions(ctx)
		list.Refresh()
	}

	list.OnSelected = func(id widget.ListItemID) {
		if id < 0 || id >= len(sessions) {
			return
		}
		currentSessionID = sessions[id].ID
		showRoleplaySession(ctx, currentSessionID, roleplaySvc, charSvc, chatArea)
	}

	newSession := widget.NewButton("+ Новая сессия", func() {
		showNewSessionDialog(ctx, roleplaySvc, charSvc, refresh)
	})

	return container.NewBorder(
		container.NewVBox(widget.NewLabelWithStyle("Ролевая игра (Roleplay)", fyne.TextAlignLeading, fyne.TextStyle{Bold: true}), widget.NewSeparator(), newSession),
		nil,
		list,
		nil,
		chatArea,
	)
}

func showRoleplaySession(ctx context.Context, sessionID int64, roleplaySvc *services.RoleplayService, charSvc *services.CharacterService, chatArea *fyne.Container) {
	dialogue, _ := roleplaySvc.GetDialogue(ctx, sessionID)

	messages := container.NewVBox()
	for _, d := range dialogue {
		icon := "👤"
		if d.Speaker == "npc" {
			icon = "🤖"
		}
		messages.Add(widget.NewLabel(icon + " " + d.Speaker + ": " + d.Message))
	}

	scroll := container.NewScroll(messages)
	scroll.SetMinSize(fyne.NewSize(400, 300))

	input := widget.NewEntry()
	input.SetPlaceHolder("Введите сообщение...")

	sendButton := widget.NewButton("Отправить", func() {
		if input.Text == "" {
			return
		}

		userMsg := &models.Dialogue{SessionID: sessionID, Speaker: "user", Message: input.Text}
		_ = roleplaySvc.SaveDialogue(ctx, userMsg)
		messages.Add(widget.NewLabel("👤 user: " + input.Text))

		text := input.Text
		input.SetText("")

		resp, err := roleplaySvc.GenerateResponse(ctx, sessionID, text)
		if err == nil {
			npcMsg := &models.Dialogue{SessionID: sessionID, Speaker: "npc", Message: resp}
			_ = roleplaySvc.SaveDialogue(ctx, npcMsg)
			messages.Add(widget.NewLabel("🤖 npc: " + resp))
			scroll.ScrollToBottom()
		}
	})

	chatArea.Objects = []fyne.CanvasObject{
		widget.NewLabel("Диалог"),
		scroll,
		container.NewHBox(input, sendButton),
	}
	chatArea.Refresh()
}

func showNewSessionDialog(ctx context.Context, roleplaySvc *services.RoleplayService, charSvc *services.CharacterService, onSave func()) {
	characters, _ := charSvc.ListCharacters(ctx)
	charNames := make([]string, len(characters))
	for i, c := range characters {
		charNames[i] = c.Name
	}

	charSelect := widget.NewSelect(charNames, nil)
	charSelect.PlaceHolder = "Выберите персонажа"

	setting := widget.NewMultiLineEntry()
	setting.SetPlaceHolder("Описание сеттинга (место, время, ситуация)")

	goals := widget.NewMultiLineEntry()
	goals.SetPlaceHolder("Ваши цели в этой сессии")

	form := widget.NewForm(
		widget.NewFormItem("Персонаж", charSelect),
		widget.NewFormItem("Сеттинг", setting),
		widget.NewFormItem("Цели", goals),
	)

	dlg := dialog.NewCustomConfirm("Новая сессия", "Начать", "Отмена", form, func(ok bool) {
		if !ok {
			return
		}

		var charID int64
		for _, c := range characters {
			if c.Name == charSelect.Selected {
				charID = c.ID
				break
			}
		}

		session := &models.RoleplaySession{CharacterID: charID, Setting: setting.Text, UserGoals: goals.Text}
		_ = roleplaySvc.CreateSession(ctx, session)
		if onSave != nil {
			onSave()
		}
	}, currentWindow())
	dlg.Resize(fyne.NewSize(500, 400))
	dlg.Show()
}
