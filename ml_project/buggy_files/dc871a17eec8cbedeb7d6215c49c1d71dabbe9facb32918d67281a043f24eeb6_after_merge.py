    def dump(self, file=None):
        from numba.six import StringIO
        nofile = file is None
        # Avoid early bind of sys.stdout as default value
        file = file or StringIO()
        for offset, block in sorted(self.blocks.items()):
            print('label %s:' % (offset,), file=file)
            block.dump(file=file)
        if nofile:
            text = file.getvalue()
            if config.HIGHLIGHT_DUMPS:
                try:
                    import pygments
                except ImportError:
                    msg = "Please install pygments to see highlighted dumps"
                    raise ValueError(msg)
                else:
                    from pygments import highlight
                    from pygments.lexers import DelphiLexer as lexer
                    from pygments.formatters import Terminal256Formatter
                    print(highlight(text, lexer(), Terminal256Formatter()))
            else:
                print(text)