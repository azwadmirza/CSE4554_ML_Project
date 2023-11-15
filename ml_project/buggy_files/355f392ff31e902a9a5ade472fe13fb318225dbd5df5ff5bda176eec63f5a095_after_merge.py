def _gen_toctree(options, subsections, parent_suff):
    options = "\n".join([f":{key}: {val}" for key, val in options.items()])

    # Generate the TOC from our options/pages
    toctree_text_md = """
    ```{{toctree}}
    :hidden:
    :titlesonly:
    {options}

    {sections}
    ```
    """
    toctree_text_rst = """
    .. toctree::
        :hidden:
        :titlesonly:
        {options}

        {sections}

    """

    if parent_suff in [".ipynb", ".md"]:
        toctree_template = toctree_text_md
    elif parent_suff == ".rst":
        toctree_template = toctree_text_rst
    else:
        return ""

    # Create the markdown directive for our toctree
    toctree = dedent(toctree_template).format(
        options=options, sections="\n".join(subsections)
    )
    return toctree