def bind(key):
    """A CompletionModel filled with all bindable commands and descriptions.

    Args:
        key: the key being bound.
    """
    model = completionmodel.CompletionModel(column_widths=(20, 60, 20))
    cmd_text = objreg.get('key-config').get_bindings_for('normal').get(key)

    if cmd_text:
        cmd_name = cmd_text.split(' ')[0]
        cmd = cmdutils.cmd_dict.get(cmd_name)
        data = [(cmd_text, cmd.desc, key)]
        model.add_category(listcategory.ListCategory("Current", data))

    cmdlist = _get_cmd_completions(include_hidden=True, include_aliases=True)
    model.add_category(listcategory.ListCategory("Commands", cmdlist))
    return model