package theme

import (
	"image/color"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/theme"
)

type customTheme struct{}

func NewTheme() fyne.Theme {
	return &customTheme{}
}

func (c *customTheme) Color(name fyne.ThemeColorName, variant fyne.ThemeVariant) color.Color {
	switch name {
	case theme.ColorNameBackground:
		return color.RGBA{R: 30, G: 30, B: 38, A: 255}
	case theme.ColorNameButton:
		return color.RGBA{R: 120, G: 81, B: 169, A: 255}
	case theme.ColorNamePrimary:
		return color.RGBA{R: 138, G: 43, B: 226, A: 255}
	case theme.ColorNameForeground:
		return color.RGBA{R: 235, G: 235, B: 245, A: 255}
	case theme.ColorNameDisabled:
		return color.RGBA{R: 100, G: 100, B: 110, A: 255}
	case theme.ColorNameFocus:
		return color.RGBA{R: 186, G: 85, B: 211, A: 255}
	case theme.ColorNameHover:
		return color.RGBA{R: 100, G: 70, B: 140, A: 255}
	case theme.ColorNameInputBackground:
		return color.RGBA{R: 40, G: 40, B: 50, A: 255}
	default:
		return theme.DefaultTheme().Color(name, variant)
	}
}

func (c *customTheme) Font(style fyne.TextStyle) fyne.Resource {
	return theme.DefaultTheme().Font(style)
}

func (c *customTheme) Icon(name fyne.ThemeIconName) fyne.Resource {
	return theme.DefaultTheme().Icon(name)
}

func (c *customTheme) Size(name fyne.ThemeSizeName) float32 {
	switch name {
	case theme.SizeNamePadding:
		return 8
	case theme.SizeNameInlineIcon:
		return 24
	default:
		return theme.DefaultTheme().Size(name)
	}
}
