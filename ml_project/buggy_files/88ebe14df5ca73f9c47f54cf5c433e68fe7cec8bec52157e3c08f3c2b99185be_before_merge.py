    def error(self, message):
        import re
        import subprocess
        from .find_commands import find_executable

        exc = sys.exc_info()[1]
        if exc:
            # this is incredibly lame, but argparse stupidly does not expose
            # reasonable hooks for customizing error handling
            if hasattr(exc, 'argument_name'):
                argument = self._get_action_from_name(exc.argument_name)
            else:
                argument = None
            if argument and argument.dest == "cmd":
                m = re.compile(r"invalid choice: '([\w\-]+)'").match(exc.message)
                if m:
                    cmd = m.group(1)
                    executable = find_executable('conda-' + cmd)
                    if not executable:
                        if cmd in build_commands:
                            raise CommandNotFoundError(cmd, '''
Error: You need to install conda-build in order to
use the "conda %s" command.''' % cmd)
                        else:
                            message = "Error: Could not locate 'conda-%s'" % cmd
                            possibilities = (set(argument.choices.keys()) |
                                             build_commands |
                                             set(find_commands()))
                            close = get_close_matches(cmd, possibilities)
                            if close:
                                message += '\n\nDid you mean one of these?\n'
                                for s in close:
                                    message += '    %s' % s
                            raise CommandNotFoundError(cmd, message)

                    args = [find_executable('conda-' + cmd)]
                    args.extend(sys.argv[2:])
                    p = subprocess.Popen(args)
                    try:
                        p.communicate()
                    except KeyboardInterrupt:
                        p.wait()
                    finally:
                        sys.exit(p.returncode)

        super(ArgumentParser, self).error(message)