def print_packages(prefix, regex=None, format='human', piplist=False,
                   json=False, show_channel_urls=context.show_channel_urls):
    if not isdir(prefix):
        raise CondaEnvironmentNotFoundError(prefix)

    if not json:
        if format == 'human':
            print('# packages in environment at %s:' % prefix)
            print('#')
        if format == 'export':
            print_export_header()

    installed = linked(prefix)
    log.debug("installed conda packages:\n%s", installed)
    if piplist and context.use_pip and format == 'human':
        other_python = get_egg_info(prefix)
        log.debug("other installed python packages:\n%s", other_python)
        installed.update(other_python)

    exitcode, output = list_packages(prefix, installed, regex, format=format,
                                     show_channel_urls=show_channel_urls)
    if not json:
        print('\n'.join(map(text_type, output)))
    else:
        stdout_json(output)
    return exitcode