def append_doc_link(help_message, path):
    if not path:
        return help_message
    doc_base = "https://man.dvc.org/"
    return "{message}\nDocumentation: <{blue}{base}{path}{nc}>".format(
        message=help_message,
        base=doc_base,
        path=path,
        blue=colorama.Fore.CYAN,
        nc=colorama.Fore.RESET,
    )