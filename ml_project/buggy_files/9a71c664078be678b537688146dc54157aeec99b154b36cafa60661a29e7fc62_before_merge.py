def _run_single_hook(hook, repo, args, write, skips=frozenset()):
    filenames = get_filenames(args, hook['files'], hook['exclude'])
    if hook['id'] in skips:
        _print_user_skipped(hook, write, args)
        return 0
    elif not filenames:
        _print_no_files_skipped(hook, write, args)
        return 0

    # Print the hook and the dots first in case the hook takes hella long to
    # run.
    write(get_hook_message(_hook_msg_start(hook, args.verbose), end_len=6))
    sys.stdout.flush()

    retcode, stdout, stderr = repo.run_hook(hook, filenames)

    if retcode != hook['expected_return_value']:
        retcode = 1
        print_color = color.RED
        pass_fail = 'Failed'
    else:
        retcode = 0
        print_color = color.GREEN
        pass_fail = 'Passed'

    write(color.format_color(pass_fail, print_color, args.color) + '\n')

    if (stdout or stderr) and (retcode or args.verbose):
        write('hookid: {0}\n'.format(hook['id']))
        write('\n')
        for output in (stdout, stderr):
            if output.strip():
                write(output.strip() + '\n')
        write('\n')

    return retcode