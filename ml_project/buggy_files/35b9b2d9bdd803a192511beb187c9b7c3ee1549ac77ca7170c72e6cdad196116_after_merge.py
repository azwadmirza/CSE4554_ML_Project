def main(argv=None):
    """Main entry point for xonsh cli."""
    args = premain(argv)
    env = builtins.__xonsh_env__
    shell = builtins.__xonsh_shell__
    if args.mode == XonshMode.single_command:
        # run a single command and exit
        run_code_with_cache(args.command.lstrip(), shell.execer, mode='single')
    elif args.mode == XonshMode.script_from_file:
        # run a script contained in a file
        if os.path.isfile(args.file):
            sys.argv = args.args
            env['ARGS'] = [args.file] + args.args
            run_script_with_cache(args.file, shell.execer, glb=shell.ctx, loc=None, mode='exec')
        else:
            print('xonsh: {0}: No such file or directory.'.format(args.file))
    elif args.mode == XonshMode.script_from_stdin:
        # run a script given on stdin
        code = sys.stdin.read()
        run_code_with_cache(code, shell.execer, glb=shell.ctx, loc=None, mode='exec')
    else:
        # otherwise, enter the shell
        env['XONSH_INTERACTIVE'] = True
        ignore_sigtstp()
        if (env['XONSH_INTERACTIVE'] and
                not env['LOADED_CONFIG'] and
                not any(os.path.isfile(i) for i in env['XONSHRC'])):
            print('Could not find xonsh configuration or run control files.')
            from xonsh import xonfig  # lazy import
            xonfig.main(['wizard', '--confirm'])
        shell.cmdloop()
    postmain(args)