    def __str__(self):
        """Provide an exception message that includes SyntaxError-like source
        line information when available.
        """
        global _hy_colored_errors

        # Syntax errors are special and annotate the traceback (instead of what
        # we would do in the message that follows the traceback).
        if isinstance(self, SyntaxError):
            return super(HyLanguageError, self).__str__()

        # When there isn't extra source information, use the normal message.
        if not isinstance(self, SyntaxError) and not self.text:
            return super(HyLanguageError, self).__str__()

        # Re-purpose Python's builtin syntax error formatting.
        output = traceback.format_exception_only(
            SyntaxError,
            SyntaxError(self.msg, (self.filename, self.lineno, self.offset,
                                   self.text)))

        arrow_idx, _ = next(((i, x) for i, x in enumerate(output)
                             if x.strip() == '^'),
                            (None, None))
        if arrow_idx:
            msg_idx = arrow_idx + 1
        else:
            msg_idx, _ = next((i, x) for i, x in enumerate(output)
                              if x.startswith('SyntaxError: '))

        # Get rid of erroneous error-type label.
        output[msg_idx] = re.sub('^SyntaxError: ', '', output[msg_idx])

        # Extend the text arrow, when given enough source info.
        if arrow_idx and self.arrow_offset:
            output[arrow_idx] = '{}{}^\n'.format(output[arrow_idx].rstrip('\n'),
                                                 '-' * (self.arrow_offset - 1))

        if _hy_colored_errors:
            from clint.textui import colored
            output[msg_idx:] = [colored.yellow(o) for o in output[msg_idx:]]
            if arrow_idx:
                output[arrow_idx] = colored.green(output[arrow_idx])
            for idx, line in enumerate(output[::msg_idx]):
                if line.strip().startswith(
                        'File "{}", line'.format(self.filename)):
                    output[idx] = colored.red(line)

        # This resulting string will come after a "<class-name>:" prompt, so
        # put it down a line.
        output.insert(0, '\n')

        # Avoid "...expected str instance, ColoredString found"
        return reduce(lambda x, y: x + y, output)