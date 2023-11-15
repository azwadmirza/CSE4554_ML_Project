def log_link_archiving_started(link: Link, link_dir: str, is_new: bool):
    # [*] [2019-03-22 13:46:45] "Log Structured Merge Trees - ben stopford"
    #     http://www.benstopford.com/2015/02/14/log-structured-merge-trees/
    #     > output/archive/1478739709

    print('\n[{symbol_color}{symbol}{reset}] [{symbol_color}{now}{reset}] "{title}"'.format(
        symbol_color=ANSI['green' if is_new else 'black'],
        symbol='+' if is_new else '√',
        now=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        title=link.title or link.base_url,
        **ANSI,
    ))
    print('    {blue}{url}{reset}'.format(url=link.url, **ANSI))
    print('    {} {}'.format(
        '>' if is_new else '√',
        pretty_path(link_dir),
    ))