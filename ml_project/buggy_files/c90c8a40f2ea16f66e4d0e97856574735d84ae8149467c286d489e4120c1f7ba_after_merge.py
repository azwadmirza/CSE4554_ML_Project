def _process_stack_cfg(cfg, stack, minion_id, pillar):
    log.debug('Config: {0}'.format(cfg))
    basedir, filename = os.path.split(cfg)
    jenv = Environment(loader=FileSystemLoader(basedir))
    jenv.globals.update({
        "__opts__": __opts__,
        "__salt__": __salt__,
        "__grains__": __grains__,
        "minion_id": minion_id,
        "pillar": pillar,
        })
    for path in _parse_stack_cfg(jenv.get_template(filename).render(stack=stack)):
        try:
            log.debug('YAML: basedir={0}, path={1}'.format(basedir, path))
            obj = yaml.safe_load(jenv.get_template(path).render(stack=stack))
            if not isinstance(obj, dict):
                log.info('Ignoring pillar stack template "{0}": Can\'t parse '
                         'as a valid yaml dictionary'.format(path))
                continue
            stack = _merge_dict(stack, obj)
        except TemplateNotFound as e:
            if hasattr(e, 'name') and e.name != path:
                log.info('Jinja include file "{0}" not found '
                         'from root dir "{1}", which was included '
                         'by stack template "{2}"'.format(
                             e.name, basedir, path))
            else:
                log.info('Ignoring pillar stack template "{0}": can\'t find from '
                         'root dir "{1}"'.format(path, basedir))
            continue
    return stack