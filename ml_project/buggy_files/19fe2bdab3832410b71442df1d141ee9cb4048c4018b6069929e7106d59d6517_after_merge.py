    def paste(self, parameter_s=''):
        """Paste & execute a pre-formatted code block from clipboard.

        The text is pulled directly from the clipboard without user
        intervention and printed back on the screen before execution (unless
        the -q flag is given to force quiet mode).

        The block is dedented prior to execution to enable execution of method
        definitions. '>' and '+' characters at the beginning of a line are
        ignored, to allow pasting directly from e-mails, diff files and
        doctests (the '...' continuation prompt is also stripped).  The
        executed block is also assigned to variable named 'pasted_block' for
        later editing with '%edit pasted_block'.

        You can also pass a variable name as an argument, e.g. '%paste foo'.
        This assigns the pasted block to variable 'foo' as string, without
        executing it (preceding >>> and + is still stripped).

        Options
        -------

          -r: re-executes the block previously entered by cpaste.

          -q: quiet mode: do not echo the pasted text back to the terminal.

        IPython statements (magics, shell escapes) are not supported (yet).

        See also
        --------
        cpaste: manually paste code into terminal until you mark its end.
        """
        opts, name = self.parse_options(parameter_s, 'rq', mode='string')
        if 'r' in opts:
            self.rerun_pasted()
            return
        try:
            block = self.shell.hooks.clipboard_get()
        except TryNext as clipboard_exc:
            message = getattr(clipboard_exc, 'args')
            if message:
                error(message[0])
            else:
                error('Could not get text from the clipboard.')
            return
        except ClipboardEmpty:
            raise UsageError("The clipboard appears to be empty")

        # By default, echo back to terminal unless quiet mode is requested
        if 'q' not in opts:
            write = self.shell.write
            write(self.shell.pycolorize(block))
            if not block.endswith('\n'):
                write('\n')
            write("## -- End pasted text --\n")

        self.store_or_execute(block, name)