    def _plot(self, title=None, window_size=DEFAULT_WINDOW_SIZE, interactive=True,
              autoclose=True, interactive_update=False, full_screen=False):
        """
        Creates plotting window

        Parameters
        ----------
        title : string, optional
            Title of plotting window.

        window_size : list, optional
            Window size in pixels.  Defaults to [1024, 768]

        interactive : bool, optional
            Enabled by default.  Allows user to pan and move figure.

        autoclose : bool, optional
            Enabled by default.  Exits plotting session when user closes the
            window when interactive is True.

        interactive_update: bool, optional
            Disabled by default.  Allows user to non-blocking draw,
            user should call Update() in each iteration.

        full_screen : bool, optional
            Opens window in full screen.  When enabled, ignores window_size.
            Default False.

        Returns
        -------
        cpos : list
            List of camera position, focal point, and view up

        """
        if title:
            self.ren_win.SetWindowName(title)

        # if full_screen:
        if full_screen:
            self.ren_win.SetFullScreen(True)
            self.ren_win.BordersOn()  # super buggy when disabled
        else:
            self.ren_win.SetSize(window_size[0], window_size[1])

        # Render
        log.debug('Rendering')
        self.ren_win.Render()

        if interactive and (not self.off_screen):
            try:  # interrupts will be caught here
                log.debug('Starting iren')
                self.iren.Initialize()
                if not interactive_update:
                    self.iren.Start()
            except KeyboardInterrupt:
                log.debug('KeyboardInterrupt')
                self.close()
                raise KeyboardInterrupt

        # Get camera position before closing
        cpos = self.camera_position

        if self.notebook:
            try:
                import IPython
            except ImportError:
                raise Exception('Install iPython to display image in a notebook')

            img = self.screenshot()
            disp = IPython.display.display(PIL.Image.fromarray(img))

        if autoclose:
            self.close()

        if self.notebook:
            return disp

        return cpos