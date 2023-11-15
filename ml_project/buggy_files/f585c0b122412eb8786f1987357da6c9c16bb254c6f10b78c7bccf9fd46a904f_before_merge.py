def apply_template_on_contents(
        contents,
        template,
        context,
        defaults,
        saltenv):
    '''
    Return the contents after applying the templating engine

    contents
        template string

    template
        template format

    context
        Overrides default context variables passed to the template.

    defaults
        Default context passed to the template.

    CLI Example:

    .. code-block:: bash

        salt '*' file.apply_template_on_contents \\
            contents='This is a {{ template }} string.' \\
            template=jinja \\
            "context={}" "defaults={'template': 'cool'}" \\
            saltenv=base
    '''
    if template in salt.utils.templates.TEMPLATE_REGISTRY:
        context_dict = defaults if defaults else {}
        if context:
            context_dict.update(context)
        # Apply templating
        contents = salt.utils.templates.TEMPLATE_REGISTRY[template](
            contents,
            from_str=True,
            to_str=True,
            context=context_dict,
            saltenv=saltenv,
            grains=__opts__['grains'],
            pillar=__pillar__,
            salt=__salt__,
            opts=__opts__)['data'].encode('utf-8')
    else:
        ret = {}
        ret['result'] = False
        ret['comment'] = ('Specified template format {0} is not supported'
                          ).format(template)
        return ret
    return contents