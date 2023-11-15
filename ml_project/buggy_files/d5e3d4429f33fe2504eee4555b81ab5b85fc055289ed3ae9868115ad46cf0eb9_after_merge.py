    def __init__(self, uid, title, url, width, height, resizable, fullscreen, min_size,
                 confirm_quit, background_color, debug, js_api, text_select, webview_ready):
        BrowserView.instances[uid] = self
        self.uid = uid

        if debug:
            BrowserView.debug = debug
            BrowserView._set_debugging()

        self.js_bridge = None
        self._file_name = None
        self._file_name_semaphore = Semaphore(0)
        self._current_url_semaphore = Semaphore(0)
        self.webview_ready = webview_ready
        self.loaded = Event()
        self.confirm_quit = confirm_quit
        self.title = title
        self.text_select = text_select

        self.is_fullscreen = False

        rect = AppKit.NSMakeRect(0.0, 0.0, width, height)
        window_mask = AppKit.NSTitledWindowMask | AppKit.NSClosableWindowMask | AppKit.NSMiniaturizableWindowMask

        if resizable:
            window_mask = window_mask | AppKit.NSResizableWindowMask

        # The allocated resources are retained because we would explicitly delete
        # this instance when its window is closed
        self.window = AppKit.NSWindow.alloc().\
            initWithContentRect_styleMask_backing_defer_(rect, window_mask, AppKit.NSBackingStoreBuffered, False).retain()
        self.window.setTitle_(title)
        self.window.setBackgroundColor_(BrowserView.nscolor_from_hex(background_color))
        self.window.setMinSize_(AppKit.NSSize(min_size[0], min_size[1]))
        self.window.setAnimationBehavior_(AppKit.NSWindowAnimationBehaviorDocumentWindow)
        BrowserView.cascade_loc = self.window.cascadeTopLeftFromPoint_(BrowserView.cascade_loc)
        # Set the titlebar color (so that it does not change with the window color)
        self.window.contentView().superview().subviews().lastObject().setBackgroundColor_(AppKit.NSColor.windowBackgroundColor())

        self.webkit = BrowserView.WebKitHost.alloc().initWithFrame_(rect).retain()

        self._browserDelegate = BrowserView.BrowserDelegate.alloc().init().retain()
        self._windowDelegate = BrowserView.WindowDelegate.alloc().init().retain()
        self._appDelegate = BrowserView.AppDelegate.alloc().init().retain()
        self.webkit.setUIDelegate_(self._browserDelegate)
        self.webkit.setFrameLoadDelegate_(self._browserDelegate)
        self.webkit.setPolicyDelegate_(self._browserDelegate)
        self.window.setDelegate_(self._windowDelegate)
        BrowserView.app.setDelegate_(self._appDelegate)

        if url:
            self.url = url
            self.load_url(url)
        else:
            self.loaded.set()

        if js_api:
            self.js_bridge = BrowserView.JSBridge.alloc().initWithObject_(js_api)

        if fullscreen:
            self.toggle_fullscreen()