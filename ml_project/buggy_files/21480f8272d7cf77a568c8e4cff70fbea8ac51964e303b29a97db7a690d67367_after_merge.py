def _run_single_hook(hook, repo, args, skips, cols):
    filenames = get_filenames(args, hook.get('files', ''), hook['exclude'])
    if hook['id'] in skips:
        output.write(get_hook_message(
            _hook_msg_start(hook, args.verbose),
            end_msg=SKIPPED,
            end_color=color.YELLOW,
            use_color=args.color,
            cols=cols,
        ))
        return 0
    elif not filenames and not hook['always_run']:
        output.write(get_hook_message(
            _hook_msg_start(hook, args.verbose),
            postfix=NO_FILES,
            end_msg=SKIPPED,
            end_color=color.TURQUOISE,
            use_color=args.color,
            cols=cols,
        ))
        return 0

    # Print the hook and the dots first in case the hook takes hella long to
    # run.
    output.write(get_hook_message(
        _hook_msg_start(hook, args.verbose), end_len=6, cols=cols,
    ))
    sys.stdout.flush()

    diff_before = cmd_output('git', 'diff', retcode=None, encoding=None)
    retcode, stdout, stderr = repo.run_hook(
        hook,
        tuple(filenames) if hook['pass_filenames'] else (),
    )
    diff_after = cmd_output('git', 'diff', retcode=None, encoding=None)

    file_modifications = diff_before != diff_after

    # If the hook makes changes, fail the commit
    if file_modifications:
        retcode = 1

    if retcode:
        retcode = 1
        print_color = color.RED
        pass_fail = 'Failed'
    else:
        retcode = 0
        print_color = color.GREEN
        pass_fail = 'Passed'

    output.write_line(color.format_color(pass_fail, print_color, args.color))

    if (stdout or stderr or file_modifications) and (retcode or args.verbose):
        output.write_line('hookid: {}\n'.format(hook['id']))

        # Print a message if failing due to file modifications
        if file_modifications:
            output.write('Files were modified by this hook.')

            if stdout or stderr:
                output.write_line(' Additional output:')

            output.write_line()

        for out in (stdout, stderr):
            assert type(out) is bytes, type(out)
            if out.strip():
                output.write_line(out.strip(), logfile_name=hook['log_file'])
        output.write_line()

    return retcode