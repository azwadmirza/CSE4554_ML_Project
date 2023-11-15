    def run_cell(self, code, cell_name, filename, run_cell_copy):
        """Run cell in current or dedicated client."""

        def norm(text):
            return remove_backslashes(to_text_string(text))

        self.run_cell_filename = filename

        # Select client to execute code on it
        client = self.get_client_for_file(filename)
        if client is None:
            client = self.get_current_client()

        is_internal_kernel = False
        if client is not None:
            # Internal kernels, use runcell
            if client.get_kernel() is not None and not run_cell_copy:
                line = (to_text_string("{}('{}','{}')")
                            .format(to_text_string('runcell'),
                                (to_text_string(cell_name).replace("\\","\\\\")
                                    .replace("'", r"\'")),
                                norm(filename).replace("'", r"\'")))
                is_internal_kernel = True

            # External kernels and run_cell_copy, just execute the code
            else:
                line = code.strip()

            try:
                if client.shellwidget._executing:
                    # Don't allow multiple executions when there's
                    # still an execution taking place
                    # Fixes issue 7293
                    pass
                elif client.shellwidget._reading:
                    client.shellwidget._append_html(
                        _("<br><b>Exit the debugger before trying to "
                          "run a cell in this console.</b>\n<hr><br>"),
                        before_prompt=True)
                    return
                else:
                    if is_internal_kernel:
                        client.shellwidget.silent_execute(
                            to_text_string('get_ipython().cell_code = '
                                           '"""{}"""')
                                .format(to_text_string(code)
                                .replace('"""', r'\"\"\"')))
                    self.execute_code(line)
            except AttributeError:
                pass
            self.visibility_changed(True)
            self.raise_()
        else:
            # XXX: not sure it can really happen
            QMessageBox.warning(self, _('Warning'),
                                _("No IPython console is currently available "
                                  "to run <b>{}</b>.<br><br>Please open a new "
                                  "one and try again."
                                  ).format(osp.basename(filename)),
                                QMessageBox.Ok)