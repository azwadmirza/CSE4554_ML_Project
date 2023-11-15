def dump(header, body):
    if config.HIGHLIGHT_DUMPS:
        try:
            import pygments
        except ImportError:
            msg = "Please install pygments to see highlighted dumps"
            raise ValueError(msg)
        else:
            from pygments import highlight
            from pygments.lexers import GasLexer as lexer
            from pygments.formatters import Terminal256Formatter
            def printer(arg):
                print(highlight(arg, lexer(),
                      Terminal256Formatter(style='solarized-light')))
    else:
        printer = print
    print('=' * 80)
    print(header.center(80, '-'))
    printer(body)
    print('=' * 80)