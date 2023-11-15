def get_jedi_script_from_document(document, locals, globals):
    try:
        return jedi.Interpreter(
            document.text,
            column=document.cursor_position_col,
            line=document.cursor_position_row + 1,
            path='input-text',
            namespaces=[locals, globals])

    except jedi.common.MultiLevelStopIteration:
        # This happens when the document is just a backslash.
        return None
    except ValueError:
        # Invalid cursor position.
        # ValueError('`column` parameter is not in a valid range.')
        return None