def watch_query(arg, **kwargs):
    usage = """Syntax: watch [seconds] [-c] query.
    * seconds: The interval at the query will be repeated, in seconds.
               By default 5.
    * -c: Clears the screen between every iteration.
"""
    if not arg:
        yield (None, None, None, usage)
        raise StopIteration
    seconds = 5
    clear_screen = False
    statement = None
    while statement is None:
        arg = arg.strip()
        if not arg:
            # Oops, we parsed all the arguments without finding a statement
            yield (None, None, None, usage)
            raise StopIteration
        (current_arg, _, arg) = arg.partition(' ')
        try:
            seconds = float(current_arg)
            continue
        except ValueError:
            pass
        if current_arg == '-c':
            clear_screen = True
            continue
        statement = '{0!s} {1!s}'.format(current_arg, arg)
    destructive_prompt = confirm_destructive_query(statement)
    if destructive_prompt is False:
        click.secho("Wise choice!")
        raise StopIteration
    elif destructive_prompt is True:
        click.secho("Your call!")
    cur = kwargs['cur']
    sql_list = [
        (sql.rstrip(';'), "> {0!s}".format(sql))
        for sql in sqlparse.split(statement)
    ]
    old_pager_enabled = is_pager_enabled()
    while True:
        if clear_screen:
            click.clear()
        try:
            # Somewhere in the code the pager its activated after every yield,
            # so we disable it in every iteration
            set_pager_enabled(False)
            for (sql, title) in sql_list:
                cur.execute(sql)
                if cur.description:
                    headers = [x[0] for x in cur.description]
                    yield (title, cur, headers, None)
                else:
                    yield (title, None, None, None)
            sleep(seconds)
        except KeyboardInterrupt:
            # This prints the Ctrl-C character in its own line, which prevents
            # to print a line with the cursor positioned behind the prompt
            click.secho("", nl=True)
            raise StopIteration
        finally:
            set_pager_enabled(old_pager_enabled)