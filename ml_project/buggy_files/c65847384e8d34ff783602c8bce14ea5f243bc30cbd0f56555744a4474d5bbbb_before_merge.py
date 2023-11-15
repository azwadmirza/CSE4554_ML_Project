    def plugin_songs(self, songs):
        value = -1
        while not 0 <= value <= 1:
            input_string = GetStringDialog(
                self.plugin_window,
                self.PLUGIN_NAME,
                _("Please give your desired rating on a scale "
                  "from 0.0 to 1.0"),
                _("_Apply"),
                Icons.NONE
            ).run()

            if input_string is None:
                return

            try:
                value = float(input_string)
            except ValueError:
                continue

        count = len(songs)
        if (count > 1 and config.getboolean("browsers",
                "rating_confirm_multiple")):
            confirm_dialog = ConfirmRateMultipleDialog(
                self.plugin_window, count, value)
            if confirm_dialog.run() != Gtk.ResponseType.YES:
                return

        for song in songs:
            song["~#rating"] = value