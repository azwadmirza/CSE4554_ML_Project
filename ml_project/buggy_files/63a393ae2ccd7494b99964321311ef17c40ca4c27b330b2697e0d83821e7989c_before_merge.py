    def __toggle_callback(self, cell, path):
        """Callback function to toggle option"""
        options.toggle(path)
        if online_update_notification_enabled:
            self.cb_beta.set_sensitive(options.get('check_online_updates'))
            if 'nt' == os.name:
                self.cb_winapp2.set_sensitive(options.get('check_online_updates'))
        if 'auto_hide' == path:
            self.cb_refresh_operations()
        if 'auto_start' == path:
            if 'nt' == os.name:
                swc = Windows.start_with_computer
            if 'posix' == os.name:
                swc = Unix.start_with_computer
            try:
                swc(options.get(path))
            except:
                traceback.print_exc()
                dlg = Gtk.MessageDialog(self.parent,
                                        type=Gtk.MessageType.ERROR,
                                        buttons=Gtk.ButtonsType.OK,
                                        message_format=str(sys.exc_info()[1]))
                dlg.run()
                dlg.destroy()