    def _querycompletions(self, completions, loc):
        """Returns whether or not we should show completions"""
        if os.path.commonprefix([c[loc:] for c in completions]):
            return True
        elif len(completions) <= builtins.__xonsh_env__.get('COMPLETION_QUERY_LIMIT'):
            return True
        msg = '\nDisplay all {} possibilities? '.format(len(completions))
        msg += '({GREEN}y{NO_COLOR} or {RED}n{NO_COLOR})'
        self.print_color(msg, end='', flush=True, file=sys.stderr)
        yn = 'x'
        while yn not in 'yn':
            yn = sys.stdin.read(1)
        show_completions = to_bool(yn)
        print()
        if not show_completions:
            rl_on_new_line()
            return False
        w, h = shutil.get_terminal_size()
        lines = columnize(completions, width=w)
        more_msg = self.format_color('{YELLOW}==={NO_COLOR} more or '
                                     '{PURPLE}({NO_COLOR}q{PURPLE}){NO_COLOR}uit '
                                     '{YELLOW}==={NO_COLOR}')
        while len(lines) > h - 1:
            print(''.join(lines[:h-1]), end='', flush=True, file=sys.stderr)
            lines = lines[h-1:]
            print(more_msg, end='', flush=True, file=sys.stderr)
            q = sys.stdin.read(1).lower()
            print(flush=True, file=sys.stderr)
            if q == 'q':
                rl_on_new_line()
                return False
        print(''.join(lines), end='', flush=True, file=sys.stderr)
        rl_on_new_line()
        return False