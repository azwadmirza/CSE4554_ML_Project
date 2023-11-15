    def __general_page(self):
        """Return a widget containing the general page"""

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        if online_update_notification_enabled:
            cb_updates = Gtk.CheckButton.new_with_label(
                _("Check periodically for software updates via the Internet"))
            cb_updates.set_active(options.get('check_online_updates'))
            cb_updates.connect(
                'toggled', self.__toggle_callback, 'check_online_updates')
            cb_updates.set_tooltip_text(
                _("If an update is found, you will be given the option to view information about it.  Then, you may manually download and install the update."))
            vbox.pack_start(cb_updates, False, True, 0)

            updates_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            updates_box.set_border_width(10)

            self.cb_beta = Gtk.CheckButton.new_with_label(label=_("Check for new beta releases"))
            self.cb_beta.set_active(options.get('check_beta'))
            self.cb_beta.set_sensitive(options.get('check_online_updates'))
            self.cb_beta.connect(
                'toggled', self.__toggle_callback, 'check_beta')
            updates_box.pack_start(self.cb_beta, False, True, 0)

            if 'nt' == os.name:
                self.cb_winapp2 = Gtk.CheckButton.new_with_label(
                    _("Download and update cleaners from community (winapp2.ini)"))
                self.cb_winapp2.set_active(options.get('update_winapp2'))
                self.cb_winapp2.set_sensitive(
                    options.get('check_online_updates'))
                self.cb_winapp2.connect(
                    'toggled', self.__toggle_callback, 'update_winapp2')
                updates_box.pack_start(self.cb_winapp2, False, True, 0)
            vbox.pack_start(updates_box, False, True, 0)

        # TRANSLATORS: This means to hide cleaners which would do
        # nothing.  For example, if Firefox were never used on
        # this system, this option would hide Firefox to simplify
        # the list of cleaners.
        cb_auto_hide = Gtk.CheckButton.new_with_label(label=_("Hide irrelevant cleaners"))
        cb_auto_hide.set_active(options.get('auto_hide'))
        cb_auto_hide.connect('toggled', self.__toggle_callback, 'auto_hide')
        vbox.pack_start(cb_auto_hide, False, True, 0)

        # TRANSLATORS: Overwriting is the same as shredding.  It is a way
        # to prevent recovery of the data. You could also translate
        # 'Shred files to prevent recovery.'
        cb_shred = Gtk.CheckButton(_("Overwrite contents of files to prevent recovery"))
        cb_shred.set_active(options.get('shred'))
        cb_shred.connect('toggled', self.__toggle_callback, 'shred')
        cb_shred.set_tooltip_text(
            _("Overwriting is ineffective on some file systems and with certain BleachBit operations.  Overwriting is significantly slower."))
        vbox.pack_start(cb_shred, False, True, 0)

        # Close the application after cleaning is complete.
        cb_exit = Gtk.CheckButton.new_with_label(label=_("Exit after cleaning"))
        cb_exit.set_active(options.get('exit_done'))
        cb_exit.connect('toggled', self.__toggle_callback, 'exit_done')
        vbox.pack_start(cb_exit, False, True, 0)

        # Disable delete confirmation message.
        cb_popup = Gtk.CheckButton(label=_("Confirm before delete"))
        cb_popup.set_active(options.get('delete_confirmation'))
        cb_popup.connect(
            'toggled', self.__toggle_callback, 'delete_confirmation')
        vbox.pack_start(cb_popup, False, True, 0)

        # Use base 1000 over 1024?
        cb_units_iec = Gtk.CheckButton(
            _("Use IEC sizes (1 KiB = 1024 bytes) instead of SI (1 kB = 1000 bytes)"))
        cb_units_iec.set_active(options.get("units_iec"))
        cb_units_iec.connect('toggled', self.__toggle_callback, 'units_iec')
        vbox.pack_start(cb_units_iec, False, True, 0)
        return vbox