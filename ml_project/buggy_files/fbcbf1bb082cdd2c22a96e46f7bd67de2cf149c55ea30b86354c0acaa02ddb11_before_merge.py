def main(database):
    history = History()
    connection = sqlite3.connect(database)

    while True:
        try:
            text = get_input('> ', lexer=SqlLexer, completer=sql_completer, style=DocumentStyle, history=history,
                             on_abort=AbortAction.RETRY)
        except EOFError:
            break  # Control-D pressed.

        with connection:
            try:
                messages = connection.execute(text)
            except Exception as e:
                print(repr(e))
            else:
                for message in messages:
                    print(message)
    print('GoodBye!')