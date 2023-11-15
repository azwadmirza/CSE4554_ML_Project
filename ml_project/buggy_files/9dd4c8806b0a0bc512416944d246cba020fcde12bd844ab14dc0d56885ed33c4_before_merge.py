def make_envvar(name):
    """Makes a StoreNonEmpty node for an environment variable."""
    env = builtins.__xonsh__.env
    vd = env.get_docs(name)
    if not vd.configurable:
        return
    default = vd.default
    if "\n" in default:
        default = "\n" + _wrap_paragraphs(default, width=69)
    curr = env.get(name)
    if is_string(curr) and is_template_string(curr):
        curr = curr.replace("{", "{{").replace("}", "}}")
    curr = pprint.pformat(curr, width=69)
    if "\n" in curr:
        curr = "\n" + curr
    msg = ENVVAR_MESSAGE.format(
        name=name,
        default=default,
        current=curr,
        docstr=_wrap_paragraphs(vd.docstr, width=69),
    )
    mnode = wiz.Message(message=msg)
    converter = env.get_converter(name)
    path = "/env/" + name
    pnode = wiz.StoreNonEmpty(
        ENVVAR_PROMPT,
        converter=converter,
        show_conversion=True,
        path=path,
        retry=True,
        store_raw=vd.store_as_str,
    )
    return mnode, pnode