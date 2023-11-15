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
        raise LexException("Could not identify the next token.", filename,
                           pos.lineno, pos.colno, source)