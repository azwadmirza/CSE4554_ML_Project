    def __catch_key(self, return_to_browser=False):
        # Catch the pressed key
        self.pressedkey = self.get_key(self.term_window)

        # Actions (available in the global hotkey dict)...
        for hotkey in self._hotkeys:
            if self.pressedkey == ord(hotkey) and 'switch' in self._hotkeys[hotkey]:
                setattr(self.args,
                        self._hotkeys[hotkey]['switch'],
                        not getattr(self.args,
                                    self._hotkeys[hotkey]['switch']))
            if self.pressedkey == ord(hotkey) and 'auto_sort' in self._hotkeys[hotkey]:
                setattr(glances_processes,
                        'auto_sort',
                        self._hotkeys[hotkey]['auto_sort'])
            if self.pressedkey == ord(hotkey) and 'sort_key' in self._hotkeys[hotkey]:
                setattr(glances_processes,
                        'sort_key',
                        self._hotkeys[hotkey]['sort_key'])

        # Other actions...
        if self.pressedkey == ord('\x1b') or self.pressedkey == ord('q'):
            # 'ESC'|'q' > Quit
            if return_to_browser:
                logger.info("Stop Glances client and return to the browser")
            else:
                self.end()
                logger.info("Stop Glances")
                sys.exit(0)
        elif self.pressedkey == ord('\n'):
            # 'ENTER' > Edit the process filter
            self.edit_filter = not self.edit_filter
        elif self.pressedkey == ord('E'):
            # 'E' > Erase the process filter
            glances_processes.process_filter = None
        elif self.pressedkey == ord('f'):
            # 'f' > Show/hide fs / folder stats
            self.args.disable_fs = not self.args.disable_fs
            self.args.disable_folders = not self.args.disable_folders
        elif self.pressedkey == ord('g'):
            # 'g' > Generate graph from history
            self.graph_tag = not self.graph_tag
        elif self.pressedkey == ord('w'):
            # 'w' > Delete finished warning logs
            glances_logs.clean()
        elif self.pressedkey == ord('x'):
            # 'x' > Delete finished warning and critical logs
            glances_logs.clean(critical=True)
        elif self.pressedkey == ord('z'):
            # 'z' > Enable or disable processes
            self.args.disable_process = not self.args.disable_process
            if self.args.disable_process:
                glances_processes.disable()
            else:
                glances_processes.enable()

        # Change the curse interface according to the current configuration
        if not self.args.enable_process_extended:
            glances_processes.disable_extended()
        else:
            glances_processes.enable_extended()

        if self.args.disable_top:
            self.disable_top()
        else:
            self.enable_top()

        if self.args.full_quicklook:
            self.enable_fullquicklook()
        else:
            self.disable_fullquicklook()

        # Return the key code
        return self.pressedkey