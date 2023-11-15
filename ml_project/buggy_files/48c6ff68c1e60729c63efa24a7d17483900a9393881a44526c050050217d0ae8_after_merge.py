def tokenize(source, filename=None):
    """ Tokenize a Lisp file or string buffer into internal Hy objects.

    Parameters
    ----------
    source: str
        The source to tokenize.
    filename: str, optional
        The filename corresponding to `source`.
    """
    from hy.lex.lexer import lexer
    from hy.lex.parser import parser
    from rply.errors import LexingError
    try:
        return parser.parse(lexer.lex(source),
                            state=ParserState(source, filename))
    except LexingError as e:
        pos = e.getsourcepos()
        raise LexException("Could not identify the next token.",
                           None, filename, source,
                           max(pos.lineno, 1),
                           max(pos.colno, 1))
    except LexException as e:
        raise e