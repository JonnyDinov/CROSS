package ui

import (
    "context"

    "aihelper/internal/services"
    customtheme "aihelper/internal/theme"
    "aihelper/internal/ui/pages"
    "fyne.io/fyne/v2"
    "fyne.io/fyne/v2/app"
    "fyne.io/fyne/v2/canvas"
    "fyne.io/fyne/v2/container"
    "fyne.io/fyne/v2/layout"
    "fyne.io/fyne/v2/theme"
    "fyne.io/fyne/v2/widget"
)

type Dependencies struct {
    Styles     *services.StyleService
    Characters *services.CharacterService
    Quests     *services.QuestService
    Books      *services.BookService
    Roleplay   *services.RoleplayService
    History    *services.HistoryService
}

type MainUI struct {
    fyneApp fyne.App
    Window  fyne.Window
    deps    Dependencies
}

type navItem struct {
    Title string
    Icon  fyne.Resource
    Build func(ctx context.Context) fyne.CanvasObject
}

func NewMainUI(deps Dependencies) *MainUI {
    fyneApp := app.NewWithID("aihelper.app")
    fyneApp.Settings().SetTheme(customtheme.NewTheme())

    window := fyneApp.NewWindow("AI Helper — Offline Editor")
    window.Resize(fyne.NewSize(1200, 800))

    ui := &MainUI{
        fyneApp: fyneApp,
        Window:  window,
        deps:    deps,
    }
    ui.build()
    return ui
}

func (m *MainUI) build() {
    ctx := context.Background()
    content := container.NewMax()

    navigation := []navItem{
        {Title: "Главное меню", Icon: theme.HomeIcon(), Build: func(ctx context.Context) fyne.CanvasObject {
            return pages.NewDashboard()
        }},
        {Title: "Быстрый редактор", Icon: theme.DocumentIcon(), Build: func(ctx context.Context) fyne.CanvasObject {
            return pages.NewQuickEditor(ctx, m.deps.Styles)
        }},
        {Title: "Менеджер стилей", Icon: theme.ContentAddIcon(), Build: func(ctx context.Context) fyne.CanvasObject {
            return pages.NewStyleManager(ctx, m.deps.Styles)
        }},
        {Title: "Персонажи", Icon: theme.AccountIcon(), Build: func(ctx context.Context) fyne.CanvasObject {
            return pages.NewCharacterManager(ctx, m.deps.Characters)
        }},
        {Title: "Генератор квестов", Icon: theme.MailComposeIcon(), Build: func(ctx context.Context) fyne.CanvasObject {
            return pages.NewQuestGenerator(ctx, m.deps.Quests, m.deps.Characters)
        }},
        {Title: "Редактор книг", Icon: theme.DocumentCreateIcon(), Build: func(ctx context.Context) fyne.CanvasObject {
            return pages.NewBookEditor(ctx, m.deps.Books)
        }},
        {Title: "Чат-редактор", Icon: theme.MailSendIcon(), Build: func(ctx context.Context) fyne.CanvasObject {
            return pages.NewChatEditor(ctx, m.deps.History, m.deps.Styles)
        }},
        {Title: "Ролевая игра", Icon: theme.VisibilityIcon(), Build: func(ctx context.Context) fyne.CanvasObject {
            return pages.NewRoleplayEngine(ctx, m.deps.Roleplay, m.deps.Characters)
        }},
    }

    list := widget.NewList(
        func() int { return len(navigation) },
        func() fyne.CanvasObject {
            icon := widget.NewIcon(nil)
            label := widget.NewLabel("")
            label.TextStyle = fyne.TextStyle{Bold: true}
            return container.NewHBox(icon, layout.NewSpacer(), label)
        },
        func(id widget.ListItemID, item fyne.CanvasObject) {
            box := item.(*fyne.Container)
            icon := box.Objects[0].(*widget.Icon)
            label := box.Objects[2].(*widget.Label)
            icon.SetResource(navigation[id].Icon)
            label.SetText(navigation[id].Title)
        },
    )

    list.OnSelected = func(id widget.ListItemID) {
        content.Objects = []fyne.CanvasObject{navigation[id].Build(ctx)}
    }

    header := canvas.NewText("AI Helper", theme.ForegroundColor())
    header.TextSize = 28
    header.Alignment = fyne.TextAlignLeading

    topBar := container.NewHBox(header, layout.NewSpacer())

    split := container.NewBorder(topBar, nil, container.NewVBox(createNavTitle("Навигация"), list), nil, content)
    m.Window.SetContent(split)
    list.Select(0)
}

func (m *MainUI) Run() {
    m.Window.ShowAndRun()
}

func createNavTitle(title string) fyne.CanvasObject {
    label := canvas.NewText(title, theme.ForegroundColor())
    label.TextSize = 14
    label.TextStyle = fyne.TextStyle{Bold: true}
    return container.NewVBox(label, widget.NewSeparator())
}
