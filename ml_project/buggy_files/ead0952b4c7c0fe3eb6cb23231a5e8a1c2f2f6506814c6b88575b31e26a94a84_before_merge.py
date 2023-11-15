def carriage_return(b, cli, *, autoindent=True):
    """Preliminary parser to determine if 'Enter' key should send command to the
    xonsh parser for execution or should insert a newline for continued input.

    Current 'triggers' for inserting a newline are:
    - Not on first line of buffer and line is non-empty
    - Previous character is a colon (covers if, for, etc...)
    - User is in an open paren-block
    - Line ends with backslash
    - Any text exists below cursor position (relevant when editing previous
    multiline blocks)
    """
    doc = b.document
    at_end_of_line = _is_blank(doc.current_line_after_cursor)
    current_line_blank = _is_blank(doc.current_line)

    indent = env.get('INDENT') if autoindent else ''

    partial_string_info = check_for_partial_string(doc.text)
    in_partial_string = (partial_string_info[0] is not None and
                         partial_string_info[1] is None)

    # indent after a colon
    if (doc.current_line_before_cursor.strip().endswith(':') and
            at_end_of_line):
        b.newline(copy_margin=autoindent)
        b.insert_text(indent, fire_event=False)
    # if current line isn't blank, check dedent tokens
    elif (not current_line_blank and
            doc.current_line.split(maxsplit=1)[0] in DEDENT_TOKENS and
            doc.line_count > 1):
        b.newline(copy_margin=autoindent)
        b.delete_before_cursor(count=len(indent))
    elif (not doc.on_first_line and not current_line_blank):
        b.newline(copy_margin=autoindent)
    elif (doc.char_before_cursor == '\\' and
            not (not builtins.__xonsh_env__.get('FORCE_POSIX_PATHS') and
                 ON_WINDOWS)):
        b.newline(copy_margin=autoindent)
    elif (doc.find_next_word_beginning() is not None and
            (any(not _is_blank(i) for i in doc.lines_from_current[1:]))):
        b.newline(copy_margin=autoindent)
    elif not current_line_blank and not can_compile(doc.text):
        b.newline(copy_margin=autoindent)
    elif current_line_blank and in_partial_string:
        b.newline(copy_margin=autoindent)
    else:
        b.accept_action.validate_and_handle(cli, b)