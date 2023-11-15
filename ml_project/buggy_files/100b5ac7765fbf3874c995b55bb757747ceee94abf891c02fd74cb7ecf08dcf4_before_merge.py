def log_shell_welcome_msg():
    from . import list_subcommands

    print('{green}# ArchiveBox Imports{reset}'.format(**ANSI))
    print('{green}from archivebox.core.models import Snapshot, User{reset}'.format(**ANSI))
    print('{green}from archivebox import *\n    {}{reset}'.format("\n    ".join(list_subcommands().keys()), **ANSI))
    print()
    print('[i] Welcome to the ArchiveBox Shell!')
    print('    https://github.com/pirate/ArchiveBox/wiki/Usage#Shell-Usage')
    print()
    print('    {lightred}Hint:{reset} Example use:'.format(**ANSI))
    print('        print(Snapshot.objects.filter(is_archived=True).count())')
    print('        Snapshot.objects.get(url="https://example.com").as_json()')
    print('        add("https://example.com/some/new/url")')