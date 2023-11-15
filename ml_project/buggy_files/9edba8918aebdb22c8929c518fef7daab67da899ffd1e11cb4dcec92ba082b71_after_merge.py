def synchronize(issue_generator, conf, main_section, dry_run=False):
    def _bool_option(section, option, default):
        try:
            return asbool(conf.get(section, option))
        except (NoSectionError, NoOptionError):
            return default

    targets = [t.strip() for t in conf.get(main_section, 'targets').split(',')]
    services = set([conf.get(target, 'service') for target in targets])
    key_list = build_key_list(services)
    uda_list = build_uda_config_overrides(services)

    if uda_list:
        log.info(
            'Service-defined UDAs exist: you can optionally use the '
            '`bugwarrior-uda` command to export a list of UDAs you can '
            'add to your taskrc file.'
        )

    static_fields = ['priority']
    if conf.has_option(main_section, 'static_fields'):
        static_fields = conf.get(main_section, 'static_fields').split(',')

    # Before running CRUD operations, call the pre_import hook(s).
    run_hooks(conf, 'pre_import')

    notify = _bool_option('notifications', 'notifications', False) and not dry_run

    tw = TaskWarriorShellout(
        config_filename=get_taskrc_path(conf, main_section),
        config_overrides=uda_list,
        marshal=True,
    )

    legacy_matching = _bool_option(main_section, 'legacy_matching', False)
    merge_annotations = _bool_option(main_section, 'merge_annotations', True)
    merge_tags = _bool_option(main_section, 'merge_tags', True)

    issue_updates = {
        'new': [],
        'existing': [],
        'changed': [],
        'closed': get_managed_task_uuids(tw, key_list, legacy_matching),
    }

    for issue in issue_generator:

        # We received this issue from The Internet, but we're not sure what
        # kind of encoding the service providers may have handed us. Let's try
        # and decode all byte strings from UTF8 off the bat.  If we encounter
        # other encodings in the wild in the future, we can revise the handling
        # here. https://github.com/ralphbean/bugwarrior/issues/350
        for key in issue.keys():
            if isinstance(issue[key], six.binary_type):
                try:
                    issue[key] = issue[key].decode('utf-8')
                except UnicodeDecodeError:
                    log.warn("Failed to interpret %r as utf-8" % key)


        try:
            existing_uuid = find_local_uuid(
                tw, key_list, issue, legacy_matching=legacy_matching
            )
            issue_dict = dict(issue)
            _, task = tw.get_task(uuid=existing_uuid)

            # Drop static fields from the upstream issue.  We don't want to
            # overwrite local changes to fields we declare static.
            for field in static_fields:
                del issue_dict[field]

            # Merge annotations & tags from online into our task object
            if merge_annotations:
                merge_left('annotations', task, issue_dict, hamming=True)

            if merge_tags:
                merge_left('tags', task, issue_dict)

            issue_dict.pop('annotations', None)
            issue_dict.pop('tags', None)

            task.update(issue_dict)

            if task.get_changes(keep=True):
                issue_updates['changed'].append(task)
            else:
                issue_updates['existing'].append(task)

            if existing_uuid in issue_updates['closed']:
                issue_updates['closed'].remove(existing_uuid)

        except MultipleMatches as e:
            log.exception("Multiple matches: %s", six.text_type(e))
        except NotFound:
            issue_updates['new'].append(dict(issue))

    notreally = ' (not really)' if dry_run else ''
    # Add new issues
    log.info("Adding %i tasks", len(issue_updates['new']))
    for issue in issue_updates['new']:
        log.info(u"Adding task %s%s", issue['description'], notreally)
        if dry_run:
            continue
        if notify:
            send_notification(issue, 'Created', conf)

        try:
            tw.task_add(**issue)
        except TaskwarriorError as e:
            log.exception("Unable to add task: %s" % e.stderr)

    log.info("Updating %i tasks", len(issue_updates['changed']))
    for issue in issue_updates['changed']:
        changes = '; '.join([
            '{field}: {f} -> {t}'.format(
                field=field,
                f=repr(ch[0]),
                t=repr(ch[1])
            )
            for field, ch in six.iteritems(issue.get_changes(keep=True))
        ])
        log.info(
            "Updating task %s, %s; %s%s",
            six.text_type(issue['uuid']),
            issue['description'],
            changes,
            notreally
        )
        if dry_run:
            continue

        try:
            tw.task_update(issue)
        except TaskwarriorError as e:
            log.exception("Unable to modify task: %s" % e.stderr)

    log.info("Closing %i tasks", len(issue_updates['closed']))
    for issue in issue_updates['closed']:
        _, task_info = tw.get_task(uuid=issue)
        log.info(
            "Completing task %s %s%s",
            issue,
            task_info.get('description', ''),
            notreally
        )
        if dry_run:
            continue

        if notify:
            send_notification(task_info, 'Completed', conf)

        try:
            tw.task_done(uuid=issue)
        except TaskwarriorError as e:
            log.exception("Unable to close task: %s" % e.stderr)

    # Send notifications
    if notify:
        only_on_new_tasks = _bool_option('notifications', 'only_on_new_tasks', False)
        if not only_on_new_tasks or len(issue_updates['new']) + len(issue_updates['changed']) + len(issue_updates['closed']) > 0:
            send_notification(
                dict(
                    description="New: %d, Changed: %d, Completed: %d" % (
                        len(issue_updates['new']),
                        len(issue_updates['changed']),
                        len(issue_updates['closed'])
                    )
                ),
                'bw_finished',
                conf,
            )