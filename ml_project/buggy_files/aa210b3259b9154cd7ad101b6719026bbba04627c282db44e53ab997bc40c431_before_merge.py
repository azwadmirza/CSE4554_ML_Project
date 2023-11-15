        def webView_didFinishLoadForFrame_(self, webview, frame):
            # Add the webview to the window if it's not yet the contentView
            i = BrowserView.get_instance('webkit', webview)

            if not webview.window():
                i.window.setContentView_(webview)
                i.window.makeFirstResponder_(webview)

                if i.js_bridge:
                    i._set_js_api()

                if not i.text_select:
                    i.webkit.windowScriptObject().evaluateWebScript_(disable_text_select)

                i.loaded.set()