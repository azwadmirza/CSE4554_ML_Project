    def _copy_create_ssl_vhost_skeleton(self, vhost, ssl_fp):
        """Copies over existing Vhost with IfModule mod_ssl.c> skeleton.

        :param obj.VirtualHost vhost: Original VirtualHost object
        :param str ssl_fp: Full path where the new ssl_vhost will reside.

        A new file is created on the filesystem.

        """
        # First register the creation so that it is properly removed if
        # configuration is rolled back
        if os.path.exists(ssl_fp):
            notes = "Appended new VirtualHost directive to file %s" % ssl_fp
            files = set()
            files.add(ssl_fp)
            self.reverter.add_to_checkpoint(files, notes)
        else:
            self.reverter.register_file_creation(False, ssl_fp)
        sift = False

        try:
            orig_contents = self._get_vhost_block(vhost)
            ssl_vh_contents, sift = self._sift_rewrite_rules(orig_contents)

            with open(ssl_fp, "a") as new_file:
                new_file.write("<IfModule mod_ssl.c>\n")
                new_file.write("\n".join(ssl_vh_contents))
                # The content does not include the closing tag, so add it
                new_file.write("</VirtualHost>\n")
                new_file.write("</IfModule>\n")
            # Add new file to augeas paths if we're supposed to handle
            # activation (it's not included as default)
            if not self.parser.parsed_in_current(ssl_fp):
                self.parser.parse_file(ssl_fp)
        except IOError:
            logger.fatal("Error writing/reading to file in make_vhost_ssl")
            raise errors.PluginError("Unable to write/read in make_vhost_ssl")

        if sift:
            reporter = zope.component.getUtility(interfaces.IReporter)
            reporter.add_message(
                "Some rewrite rules copied from {0} were disabled in the "
                "vhost for your HTTPS site located at {1} because they have "
                "the potential to create redirection loops.".format(
                    vhost.filep, ssl_fp), reporter.MEDIUM_PRIORITY)
        self.aug.set("/augeas/files%s/mtime" % (self._escape(ssl_fp)), "0")
        self.aug.set("/augeas/files%s/mtime" % (self._escape(vhost.filep)), "0")