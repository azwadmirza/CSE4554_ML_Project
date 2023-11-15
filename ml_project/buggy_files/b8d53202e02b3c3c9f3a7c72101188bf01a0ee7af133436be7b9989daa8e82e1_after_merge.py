def create_window(uid, title, url, width, height, resizable, fullscreen, min_size,
                  confirm_quit, background_color, debug, js_api, text_select, webview_ready):
    def create():
        window = BrowserView.BrowserForm(uid, title, url, width, height, resizable, fullscreen,
                                         min_size, confirm_quit, background_color, debug, js_api,
                                         text_select, webview_ready)
        BrowserView.instances[uid] = window
        window.Show()

        if uid == 'master':
            app.Run()

    webview_ready.clear()
    app = WinForms.Application

    if uid == 'master':
        set_ie_mode()
        if sys.getwindowsversion().major >= 6:
            windll.user32.SetProcessDPIAware()

        app.EnableVisualStyles()
        app.SetCompatibleTextRenderingDefault(False)

        thread = Thread(ThreadStart(create))
        thread.SetApartmentState(ApartmentState.STA)
        thread.Start()
        thread.Join()
    else:
        i = list(BrowserView.instances.values())[0]     # arbitrary instance
        i.Invoke(Func[Type](create))