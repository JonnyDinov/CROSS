package pages

import "fyne.io/fyne/v2"

func currentWindow() fyne.Window {
	app := fyne.CurrentApp()
	if app == nil {
		return nil
	}
	windows := app.Driver().AllWindows()
	if len(windows) > 0 {
		return windows[0]
	}
	return nil
}
