def open_page_in_browser(url):
    import subprocess
    import webbrowser
    platform_name, release = _get_platform_info()

    if _is_wsl(platform_name, release):   # windows 10 linux subsystem
        try:
            return subprocess.call(['cmd.exe', '/c', "start {}".format(url.replace('&', '^&'))])
        except FileNotFoundError:  # WSL might be too old
            pass
    elif platform_name == 'darwin':
        # handle 2 things:
        # a. On OSX sierra, 'python -m webbrowser -t <url>' emits out "execution error: <url> doesn't
        #    understand the "open location" message"
        # b. Python 2.x can't sniff out the default browser
        return subprocess.Popen(['open', url])
    return webbrowser.open(url, new=2)  # 2 means: open in a new tab, if possible