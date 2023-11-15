    def _get_new_completion(self, before_cursor, under_cursor):
        """Get the completion function based on the current command text.

        Args:
            before_cursor: The command chunks before the cursor.
            under_cursor: The command chunk under the cursor.

        Return:
            A completion model.
        """
        if '--' in before_cursor or under_cursor.startswith('-'):
            # cursor on a flag or after an explicit split (--)
            return None
        log.completion.debug("Before removing flags: {}".format(before_cursor))
        if not before_cursor:
            # '|' or 'set|'
            log.completion.debug('Starting command completion')
            return miscmodels.command
        try:
            cmd = cmdutils.cmd_dict[before_cursor[0]]
        except KeyError:
            log.completion.debug("No completion for unknown command: {}"
                                 .format(before_cursor[0]))
            return None

        before_cursor = [x for x in before_cursor if not x.startswith('-')]
        log.completion.debug("After removing flags: {}".format(before_cursor))
        argpos = len(before_cursor) - 1
        try:
            func = cmd.get_pos_arg_info(argpos).completion
        except IndexError:
            log.completion.debug("No completion in position {}".format(argpos))
            return None
        return func