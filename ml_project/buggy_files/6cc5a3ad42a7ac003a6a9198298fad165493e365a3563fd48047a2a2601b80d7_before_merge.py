def numeric_phrase(singular, plural, n, template_var=None):
    """Returns a final locale-specific phrase with pluralisation if necessary
    and grouping of the number.

    This is added to custom gettext keywords to allow us to use as-is.

    Args:
        singular (text_type)
        plural (text_type)
        n (int)
        template_var (text_type)
    Returns:
        text_type

    For example,

    ``numeric_phrase('Add %d song', 'Add %d songs', 12345)``
    returns
    `"Add 12,345 songs"`
    (in `en_US` locale at least)
    """
    num_text = locale.format('%d', n, grouping=True)
    if not template_var:
        template_var = '%d'
        replacement = '%s'
        params = num_text
    else:
        template_var = '%(' + template_var + ')d'
        replacement = '%(' + template_var + ')s'
        params = dict()
        params[template_var] = num_text
    return (ngettext(singular.replace(template_var, replacement),
            plural.replace(template_var, replacement), n) % params)