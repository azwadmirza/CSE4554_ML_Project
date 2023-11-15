    def perform_start_download_request(self, uri, anon_download, safe_seeding, destination, selected_files,
                                       total_files=0, callback=None):
        # Check if destination directory is writable
        if not is_dir_writable(destination):
            ConfirmationDialog.show_message(self.window(), "Download error <i>%s</i>" % uri,
                                            "Insufficient write permissions to <i>%s</i> directory. "
                                            "Please add proper write permissions on the directory and "
                                            "add the torrent again." % destination, "OK")
            return

        selected_files_uri = ""
        if len(selected_files) != total_files:  # Not all files included
            selected_files_uri = u'&' + u''.join(u"selected_files[]=%s&" %
                                                 quote_plus_unicode(filename) for filename in selected_files)[:-1]

        anon_hops = int(self.tribler_settings['Tribler']['default_number_hops']) if anon_download else 0
        safe_seeding = 1 if safe_seeding else 0
        post_data = "uri=%s&anon_hops=%d&safe_seeding=%d&destination=%s%s" % (quote_plus_unicode(uri), anon_hops,
                                                                              safe_seeding, destination,
                                                                              selected_files_uri)
        post_data = post_data.encode('utf-8')  # We need to send bytes in the request, not unicode

        request_mgr = TriblerRequestManager()
        request_mgr.perform_request("downloads", callback if callback else self.on_download_added,
                                    method='PUT', data=post_data)

        # Save the download location to the GUI settings
        current_settings = get_gui_setting(self.gui_settings, "recent_download_locations", "")
        recent_locations = current_settings.split(",") if len(current_settings) > 0 else []
        if isinstance(destination, unicode):
            destination = destination.encode('utf-8')
        encoded_destination = destination.encode('hex')
        if encoded_destination in recent_locations:
            recent_locations.remove(encoded_destination)
        recent_locations.insert(0, encoded_destination)

        if len(recent_locations) > 5:
            recent_locations = recent_locations[:5]

        self.gui_settings.setValue("recent_download_locations", ','.join(recent_locations))