def dump_html(filename, html_text):
    isDumpEnabled = True
    filename = sanitize_filename(filename)
    if _config is not None:
        isDumpEnabled = _config.enableDump
        if _config.enableDump:
            if len(_config.skipDumpFilter) > 0:
                matchResult = re.findall(_config.skipDumpFilter, filename)
                if matchResult is not None and len(matchResult) > 0:
                    isDumpEnabled = False

    if html_text is not None and len(html_text) == 0:
        print_and_log('info', 'Empty Html.')
        return ""

    if isDumpEnabled:
        try:
            dump = open(filename, 'wb', encoding="utf-8")
            dump.write(str(html_text))
            dump.close()
            return filename
        except IOError as ex:
            print_and_log('error', str(ex))
        print_and_log("info", "Dump File created: {0}".format(filename))
    else:
        print_and_log('info', 'Dump not enabled.')
    return ""