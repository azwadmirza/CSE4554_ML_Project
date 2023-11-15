def search_module_help(text):
    """
    Search the help for a string

    :param text: find text in the module help using case-insensitive matching
    :return: an html document of all the module help pages that matched or None if no match found.
    """
    matching_help = []

    count = 0

    for menu_item, help_text in MENU_HELP.iteritems():
        help_text = cellprofiler.gui.html.utils.rst_to_html_fragment(help_text)

        matches = __search_fn(help_text, text)

        if len(matches) > 0:
            matching_help.append((menu_item, help_text, matches))

            count += len(matches)

    for module_name in cellprofiler.modules.get_module_names():
        module = cellprofiler.modules.instantiate_module(module_name)

        location = os.path.split(module.create_settings.im_func.func_code.co_filename)[0]

        if location == cellprofiler.preferences.get_plugin_directory():
            continue

        help_text = module.get_help()

        matches = __search_fn(help_text, text)

        if len(matches) > 0:
            matching_help.append((module_name, help_text, matches))

            count += len(matches)

    if len(matching_help) == 0:
        return None

    top = u"""\
<html style="font-family:arial">
<head>
    <title>{count} match{es} found</title>
</head>
<body>
    <h1>Match{es} found ({count} total)</h1><br>
    <ul></ul>
</body>
</html>
""".format(**{
        "count": count,
        "es": u"" if count == 1 else u"es"
    })

    body = u"<br>"

    match_num = 1

    prev_link = u"""<a href="#match%d" title="Previous match"><img alt="previous match" src="memory:previous.png"></a>"""

    anchor = u"""<a name="match%d"><u>%s</u></a>"""

    next_link = u"""<a href="#match%d" title="Next match"><img src="memory:next.png" alt="next match"></a>"""

    for title, help_text, pairs in matching_help:
        top += u"""<li><a href="#match{:d}">{}</a></li>\n""".format(match_num, title)

        start_match = re.search(r"<\s*body[^>]*?>", help_text, re.IGNORECASE)

        # Some pages don't have in-line titles
        # Not matching "<h1>" here for cases that have "<h1 class='title'>", etc.
        if not help_text.startswith(u"<h1"):
            body += u"<h1>{}</h1>".format(title)

        if start_match is None:
            start = 0
        else:
            start = start_match.end()

        end_match = re.search(r"<\\\s*body", help_text, re.IGNORECASE)

        if end_match is None:
            end = len(help_text)
        else:
            end = end_match.start()

        for begin_pos, end_pos in pairs:
            body += help_text[start:begin_pos]

            if match_num > 1:
                body += prev_link % (match_num - 1)

            body += anchor % (match_num, help_text[begin_pos:end_pos])

            if match_num != count:
                body += next_link % (match_num + 1)

            start = end_pos

            match_num += 1

        body += help_text[start:end] + u"<br>"

    result = u"{}</ul><br>\n{}</body></html>".format(top, body)

    return result