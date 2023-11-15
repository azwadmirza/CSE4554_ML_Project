def create_apache_identifier(name):
    """
    By convention if a module is loaded via name, it appears in apache2ctl -M as
    name_module.

    Some modules don't follow this convention and we use replacements for those."""

    # a2enmod name replacement to apache2ctl -M names
    text_workarounds = [
        ('shib2', 'mod_shib'),
        ('evasive', 'evasive20_module'),
    ]

    # re expressions to extract subparts of names
    re_workarounds = [
        ('php', r'^(php\d)\.'),
    ]

    for a2enmod_spelling, module_name in text_workarounds:
        if a2enmod_spelling in name:
            return module_name

    for search, reexpr in re_workarounds:
        if search in name:
            rematch = re.search(reexpr, name)
            return rematch.group(1) + '_module'

    return name + '_module'