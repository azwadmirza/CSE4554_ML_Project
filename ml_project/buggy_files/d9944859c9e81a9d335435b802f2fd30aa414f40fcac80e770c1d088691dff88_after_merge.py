def log_removal_started(links: List["Link"], yes: bool, delete: bool):
    print('{lightyellow}[i] Found {} matching URLs to remove.{reset}'.format(len(links), **ANSI))
    if delete:
        file_counts = [link.num_outputs for link in links if os.path.exists(link.link_dir)]
        print(
            f'    {len(links)} Links will be de-listed from the main index, and their archived content folders will be deleted from disk.\n'
            f'    ({len(file_counts)} data folders with {sum(file_counts)} archived files will be deleted!)'
        )
    else:
        print(
            f'    Matching links will be de-listed from the main index, but their archived content folders will remain in place on disk.\n'
            f'    (Pass --delete if you also want to permanently delete the data folders)'
        )

    if not yes:
        print()
        print('{lightyellow}[?] Do you want to proceed with removing these {} links?{reset}'.format(len(links), **ANSI))
        try:
            assert input('    y/[n]: ').lower() == 'y'
        except (KeyboardInterrupt, EOFError, AssertionError):
            raise SystemExit(0)