def extract_lambda_source(f):
    """Extracts a single lambda expression from the string source. Returns a
    string indicating an unknown body if it gets confused in any way.

    This is not a good function and I am sorry for it. Forgive me my
    sins, oh lord
    """
    argspec = getfullargspec(f)
    arg_strings = []
    # In Python 2 you can have destructuring arguments to functions. This
    # results in an argspec with non-string values. I'm not very interested in
    # handling these properly, but it's important to not crash on them.
    bad_lambda = False
    for a in argspec.args:
        if isinstance(a, (tuple, list)):  # pragma: no cover
            arg_strings.append("(%s)" % (", ".join(a),))
            bad_lambda = True
        else:
            assert isinstance(a, str)
            arg_strings.append(a)
    if argspec.varargs:
        arg_strings.append("*" + argspec.varargs)
    elif argspec.kwonlyargs:
        arg_strings.append("*")
    for a in argspec.kwonlyargs or []:
        default = (argspec.kwonlydefaults or {}).get(a)
        if default:
            arg_strings.append("{}={}".format(a, default))
        else:
            arg_strings.append(a)

    if_confused = "lambda %s: <unknown>" % (", ".join(arg_strings),)
    if bad_lambda:  # pragma: no cover
        return if_confused
    try:
        source = inspect.getsource(f)
    except IOError:
        return if_confused

    source = LINE_CONTINUATION.sub(" ", source)
    source = WHITESPACE.sub(" ", source)
    source = source.strip()
    assert "lambda" in source

    tree = None

    try:
        tree = ast.parse(source)
    except SyntaxError:
        for i in hrange(len(source) - 1, len("lambda"), -1):
            prefix = source[:i]
            if "lambda" not in prefix:
                break
            try:
                tree = ast.parse(prefix)
                source = prefix
                break
            except SyntaxError:
                continue
    if tree is None:
        if source.startswith("@"):
            # This will always eventually find a valid expression because
            # the decorator must be a valid Python function call, so will
            # eventually be syntactically valid and break out of the loop. Thus
            # this loop can never terminate normally, so a no branch pragma is
            # appropriate.
            for i in hrange(len(source) + 1):  # pragma: no branch
                p = source[1:i]
                if "lambda" in p:
                    try:
                        tree = ast.parse(p)
                        source = p
                        break
                    except SyntaxError:
                        pass

    if tree is None:
        return if_confused

    all_lambdas = extract_all_lambdas(tree)
    aligned_lambdas = [l for l in all_lambdas if args_for_lambda_ast(l) == argspec.args]
    if len(aligned_lambdas) != 1:
        return if_confused
    lambda_ast = aligned_lambdas[0]
    assert lambda_ast.lineno == 1

    # If the source code contains Unicode characters, the bytes of the original
    # file don't line up with the string indexes, and `col_offset` doesn't match
    # the string we're using.  We need to convert the source code into bytes
    # before slicing.
    #
    # Under the hood, the inspect module is using `tokenize.detect_encoding` to
    # detect the encoding of the original source file.  We'll use the same
    # approach to get the source code as bytes.
    #
    # See https://github.com/HypothesisWorks/hypothesis/issues/1700 for an
    # example of what happens if you don't correct for this.
    #
    # Note: if the code doesn't come from a file (but, for example, a doctest),
    # `getsourcefile` will return `None` and the `open()` call will fail with
    # an OSError.  Or if `f` is a built-in function, in which case we get a
    # TypeError.  In both cases, fall back to splitting the Unicode string.
    # It's not perfect, but it's the best we can do.
    #
    # Note 2: You can only detect the encoding with `tokenize.detect_encoding`
    # in Python 3.2 or later.  But that's okay, because the only version that
    # affects for us is Python 2.7, and 2.7 doesn't support non-ASCII identifiers:
    # https://www.python.org/dev/peps/pep-3131/. In this case we'll get an
    # AttributeError.
    #
    try:
        encoding, _ = tokenize.detect_encoding(
            open(inspect.getsourcefile(f), "rb").readline
        )
        source_bytes = source.encode(encoding)
        source_bytes = source_bytes[lambda_ast.col_offset :].strip()
        source = source_bytes.decode(encoding)
    except (AttributeError, OSError, TypeError):
        source = source[lambda_ast.col_offset :].strip()

    # This ValueError can be thrown in Python 3 if:
    #
    #  - There's a Unicode character in the line before the Lambda, and
    #  - For some reason we can't detect the source encoding of the file
    #
    # because slicing on `lambda_ast.col_offset` will account for bytes, but
    # the slice will be on Unicode characters.
    #
    # In practice this seems relatively rare, so we just give up rather than
    # trying to recover.
    try:
        source = source[source.index("lambda") :]
    except ValueError:
        return if_confused

    for i in hrange(len(source), len("lambda"), -1):  # pragma: no branch
        try:
            parsed = ast.parse(source[:i])
            assert len(parsed.body) == 1
            assert parsed.body
            if isinstance(parsed.body[0].value, ast.Lambda):
                source = source[:i]
                break
        except SyntaxError:
            pass
    lines = source.split("\n")
    lines = [PROBABLY_A_COMMENT.sub("", l) for l in lines]
    source = "\n".join(lines)

    source = WHITESPACE.sub(" ", source)
    source = SPACE_FOLLOWS_OPEN_BRACKET.sub("(", source)
    source = SPACE_PRECEDES_CLOSE_BRACKET.sub(")", source)
    source = source.strip()
    return source