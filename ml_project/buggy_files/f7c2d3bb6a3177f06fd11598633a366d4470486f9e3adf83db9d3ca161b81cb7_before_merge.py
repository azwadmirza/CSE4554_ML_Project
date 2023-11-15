    def start(self,  # pylint: disable=keyword-arg-before-vararg
              group=webelem.Group.all, target=Target.normal,
              *args, win_id, mode=None, add_history=False, rapid=False):
        """Start hinting.

        Args:
            rapid: Whether to do rapid hinting. With rapid hinting, the hint
                   mode isn't left after a hint is followed, so you can easily
                   open multiple links. This is only possible with targets
                   `tab` (with `tabs.background_tabs=true`), `tab-bg`,
                   `window`, `run`, `hover`, `userscript` and `spawn`.
            add_history: Whether to add the spawned or yanked link to the
                         browsing history.
            group: The element types to hint.

                - `all`: All clickable elements.
                - `links`: Only links.
                - `images`: Only images.
                - `inputs`: Only input fields.

            target: What to do with the selected element.

                - `normal`: Open the link.
                - `current`: Open the link in the current tab.
                - `tab`: Open the link in a new tab (honoring the
                         `tabs.background_tabs` setting).
                - `tab-fg`: Open the link in a new foreground tab.
                - `tab-bg`: Open the link in a new background tab.
                - `window`: Open the link in a new window.
                - `hover` : Hover over the link.
                - `yank`: Yank the link to the clipboard.
                - `yank-primary`: Yank the link to the primary selection.
                - `run`: Run the argument as command.
                - `fill`: Fill the commandline with the command given as
                          argument.
                - `download`: Download the link.
                - `userscript`: Call a userscript with `$QUTE_URL` set to the
                                link.
                - `spawn`: Spawn a command.

            mode: The hinting mode to use.

                - `number`: Use numeric hints.
                - `letter`: Use the chars in the hints.chars setting.
                - `word`: Use hint words based on the html elements and the
                          extra words.

            *args: Arguments for spawn/userscript/run/fill.

                - With `spawn`: The executable and arguments to spawn.
                                `{hint-url}` will get replaced by the selected
                                URL.
                - With `userscript`: The userscript to execute. Either store
                                     the userscript in
                                     `~/.local/share/qutebrowser/userscripts`
                                     (or `$XDG_DATA_DIR`), or use an absolute
                                     path.
                - With `fill`: The command to fill the statusbar with.
                                `{hint-url}` will get replaced by the selected
                                URL.
                - With `run`: Same as `fill`.
        """
        tabbed_browser = objreg.get('tabbed-browser', scope='window',
                                    window=self._win_id)
        tab = tabbed_browser.currentWidget()
        if tab is None:
            raise cmdexc.CommandError("No WebView available yet!")

        mode_manager = objreg.get('mode-manager', scope='window',
                                  window=self._win_id)
        if mode_manager.mode == usertypes.KeyMode.hint:
            modeman.leave(win_id, usertypes.KeyMode.hint, 're-hinting')

        if rapid:
            if target in [Target.tab_bg, Target.window, Target.run,
                          Target.hover, Target.userscript, Target.spawn,
                          Target.download, Target.normal, Target.current]:
                pass
            elif target == Target.tab and config.val.tabs.background:
                pass
            else:
                name = target.name.replace('_', '-')
                raise cmdexc.CommandError("Rapid hinting makes no sense with "
                                          "target {}!".format(name))

        if mode is None:
            mode = config.val.hints.mode

        self._check_args(target, *args)
        self._context = HintContext()
        self._context.tab = tab
        self._context.target = target
        self._context.rapid = rapid
        self._context.hint_mode = mode
        self._context.add_history = add_history
        try:
            self._context.baseurl = tabbed_browser.current_url()
        except qtutils.QtValueError:
            raise cmdexc.CommandError("No URL set for this page yet!")
        self._context.args = args
        self._context.group = group
        selector = webelem.SELECTORS[self._context.group]
        self._context.tab.elements.find_css(selector, self._start_cb,
                                            only_visible=True)