    def flush_errors(new_messages: List[str], serious: bool) -> None:
        if options.pretty:
            new_messages = formatter.fit_in_terminal(new_messages)
        messages.extend(new_messages)
        f = stderr if serious else stdout
        try:
            for msg in new_messages:
                if options.color_output:
                    msg = formatter.colorize(msg)
                f.write(msg + '\n')
            f.flush()
        except BrokenPipeError:
            sys.exit(2)