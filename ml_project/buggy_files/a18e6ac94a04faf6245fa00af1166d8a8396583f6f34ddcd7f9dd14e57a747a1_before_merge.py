    def __str__(self):

        line = self.expression.start_line
        start = self.expression.start_column
        end = self.expression.end_column

        source = []
        if self.source is not None:
            source = self.source.split("\n")[line-1:self.expression.end_line]

            if line == self.expression.end_line:
                length = end - start
            else:
                length = len(source[0]) - start

        result = ""

        result += '  File "%s", line %d, column %d\n\n' % (self.filename,
                                                           line,
                                                           start)

        if len(source) == 1:
            result += '  %s\n' % colored.red(source[0])
            result += '  %s%s\n' % (' '*(start-1),
                                    colored.green('^' + '-'*(length-1) + '^'))
        if len(source) > 1:
            result += '  %s\n' % colored.red(source[0])
            result += '  %s%s\n' % (' '*(start-1),
                                    colored.green('^' + '-'*length))
            if len(source) > 2:  # write the middle lines
                for line in source[1:-1]:
                    result += '  %s\n' % colored.red("".join(line))
                    result += '  %s\n' % colored.green("-"*len(line))

            # write the last line
            result += '  %s\n' % colored.red("".join(source[-1]))
            result += '  %s\n' % colored.green('-'*(end-1) + '^')

        result += colored.yellow("%s: %s\n\n" %
                                 (self.__class__.__name__,
                                  self.message))

        if not PY3:
            return result.encode('utf-8')
        else:
            return result