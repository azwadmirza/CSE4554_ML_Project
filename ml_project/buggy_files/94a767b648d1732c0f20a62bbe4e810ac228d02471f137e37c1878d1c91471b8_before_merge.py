def change(name, context=None, changes=None, lens=None,
        load_path=None, **kwargs):
    '''
    .. versionadded:: 2014.7.0

    This state replaces :py:func:`~salt.states.augeas.setvalue`.

    Issue changes to Augeas, optionally for a specific context, with a
    specific lens.

    name
        State name

    context
        A file path, prefixed by ``/files``. Should resolve to an actual file
        (not an arbitrary augeas path). This is used to avoid duplicating the
        file name for each item in the changes list (for example, ``set bind 0.0.0.0``
        in the example below operates on the file specified by ``context``). If
        ``context`` is not specified, a file path prefixed by ``/files`` should be
        included with the ``set`` command.

        The file path is examined to determine if the
        specified changes are already present.

        .. code-block:: yaml

            redis-conf:
              augeas.change:
                - context: /files/etc/redis/redis.conf
                - changes:
                  - set bind 0.0.0.0
                  - set maxmemory 1G

    changes
        List of changes that are issued to Augeas. Available commands are
        ``set``, ``setm``, ``mv``/``move``, ``ins``/``insert``, and
        ``rm``/``remove``.

    lens
        The lens to use, needs to be suffixed with `.lns`, e.g.: `Nginx.lns`.
        See the `list of stock lenses <http://augeas.net/stock_lenses.html>`_
        shipped with Augeas.

    .. versionadded:: 2016.3.0

    load_path
        A list of directories that modules should be searched in. This is in
        addition to the standard load path and the directories in
        AUGEAS_LENS_LIB.


    Usage examples:

    Set the ``bind`` parameter in ``/etc/redis/redis.conf``:

    .. code-block:: yaml

        redis-conf:
          augeas.change:
            - changes:
              - set /files/etc/redis/redis.conf/bind 0.0.0.0

    .. note::

        Use the ``context`` parameter to specify the file you want to
        manipulate. This way you don't have to include this in the changes
        every time:

        .. code-block:: yaml

            redis-conf:
              augeas.change:
                - context: /files/etc/redis/redis.conf
                - changes:
                  - set bind 0.0.0.0
                  - set databases 4
                  - set maxmemory 1G

    Augeas is aware of a lot of common configuration files and their syntax.
    It knows the difference between for example ini and yaml files, but also
    files with very specific syntax, like the hosts file. This is done with
    *lenses*, which provide mappings between the Augeas tree and the file.

    There are many `preconfigured lenses`_ that come with Augeas by default,
    and they specify the common locations for configuration files. So most
    of the time Augeas will know how to manipulate a file. In the event that
    you need to manipulate a file that Augeas doesn't know about, you can
    specify the lens to use like this:

    .. code-block:: yaml

        redis-conf:
          augeas.change:
            - lens: redis
            - context: /files/etc/redis/redis.conf
            - changes:
              - set bind 0.0.0.0

    .. note::

        Even though Augeas knows that ``/etc/redis/redis.conf`` is a Redis
        configuration file and knows how to parse it, it is recommended to
        specify the lens anyway. This is because by default, Augeas loads all
        known lenses and their associated file paths. All these files are
        parsed when Augeas is loaded, which can take some time. When specifying
        a lens, Augeas is loaded with only that lens, which speeds things up
        quite a bit.

    .. _preconfigured lenses: http://augeas.net/stock_lenses.html

    A more complex example, this adds an entry to the services file for Zabbix,
    and removes an obsolete service:

    .. code-block:: yaml

        zabbix-service:
          augeas.change:
            - lens: services
            - context: /files/etc/services
            - changes:
              - ins service-name after service-name[last()]
              - set service-name[last()] zabbix-agent
              - set service-name[. = 'zabbix-agent']/#comment "Zabbix Agent service"
              - set service-name[. = 'zabbix-agent']/port 10050
              - set service-name[. = 'zabbix-agent']/protocol tcp
              - rm service-name[. = 'im-obsolete']
            - unless: grep "zabbix-agent" /etc/services

    .. warning::

        Don't forget the ``unless`` here, otherwise a new entry will be added
        every time this state is run.

    '''
    ret = {'name': name, 'result': False, 'comment': '', 'changes': {}}

    if not changes or not isinstance(changes, list):
        ret['comment'] = '\'changes\' must be specified as a list'
        return ret

    if load_path is not None:
        if not isinstance(load_path, list):
            ret['comment'] = '\'load_path\' must be specified as a list'
            return ret
        else:
            load_path = ':'.join(load_path)

    filename = None
    if context is None:
        try:
            filename = _check_filepath(changes)
        except ValueError as err:
            ret['comment'] = 'Error: {0}'.format(str(err))
            return ret
    else:
        filename = re.sub('^/files|/$', '', context)

    if __opts__['test']:
        ret['result'] = True
        ret['comment'] = 'Executing commands'
        if context:
            ret['comment'] += ' in file "{0}":\n'.format(context)
        ret['comment'] += "\n".join(changes)
        return ret

    old_file = []
    if filename is not None:
        if os.path.isfile(filename):
            with salt.utils.fopen(filename, 'r') as file_:
                old_file = file_.readlines()

    result = __salt__['augeas.execute'](
        context=context, lens=lens,
        commands=changes, load_path=load_path)
    ret['result'] = result['retval']

    if ret['result'] is False:
        ret['comment'] = 'Error: {0}'.format(result['error'])
        return ret

    if old_file:
        with salt.utils.fopen(filename, 'r') as file_:
            diff = ''.join(
                difflib.unified_diff(old_file, file_.readlines(), n=0))

        if diff:
            ret['comment'] = 'Changes have been saved'
            ret['changes'] = {'diff': diff}
        else:
            ret['comment'] = 'No changes made'

    else:
        ret['comment'] = 'Changes have been saved'
        ret['changes'] = {'updates': changes}

    return ret