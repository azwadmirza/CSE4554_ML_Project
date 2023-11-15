    def run_cell(self, code, cell_name, filename, run_cell_copy,
                 function='runcell'):
        """Run cell in current or dedicated client."""

        def norm(text):
            return remove_backslashes(to_text_string(text))

        self.run_cell_filename = filename

        # Select client to execute code on it
        client = self.get_client_for_file(filename)
        if client is None:
            client = self.get_current_client()

        if client is not None:
            # Internal kernels, use runcell
            if client.get_kernel() is not None and not run_cell_copy:
                line = (to_text_string(
                        "{}({}, '{}')").format(
                                to_text_string(function),
                                repr(cell_name),
                                norm(filename).replace("'", r"\'")))

            # External kernels and run_cell_copy, just execute the code
            else:
                line = code.strip()

            try:
                if client.shellwidget._executing:
                    # Don't allow multiple executions when there's
                    # still an execution taking place
                    # Fixes spyder-ide/spyder#7293.
                    pass
                elif (client.shellwidget._reading and
                      client.shellwidget.is_debugging()):
                    client.shellwidget.write_to_stdin('!' + line)
                else:
                    self.execute_code(line)
            except AttributeError:
                pass
            self._visibility_changed(True)
            self.raise_()
        else:
            # XXX: not sure it can really happen
            QMessageBox.warning(self, _('Warning'),
                                _("No IPython console is currently available "
                                  "to run <b>{}</b>.<br><br>Please open a new "
                                  "one and try again."
                                  ).format(osp.basename(filename)),
                                QMessageBox.Ok)