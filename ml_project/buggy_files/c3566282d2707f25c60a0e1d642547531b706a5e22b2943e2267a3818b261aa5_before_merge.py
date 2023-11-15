    def __str__(self):
        global _hy_colored_errors

        output = traceback.format_exception_only(SyntaxError,
                                                 SyntaxError(*self.args))

        if _hy_colored_errors:
            from hy.errors import colored
            output[-1] = colored.yellow(output[-1])
            if len(self.source) > 0:
                output[-2] = colored.green(output[-2])
                for line in output[::-2]:
                    if line.strip().startswith(
                            'File "{}", line'.format(self.filename)):
                        break
                output[-3] = colored.red(output[-3])

        # Avoid "...expected str instance, ColoredString found"
        return reduce(lambda x, y: x + y, output)