def apply_(mods=None, **kwargs):
    '''
    .. versionadded:: 2015.5.0

    This function will call :mod:`state.highstate
    <salt.modules.state.highstate>` or :mod:`state.sls
    <salt.modules.state.sls>` based on the arguments passed to this function.
    It exists as a more intuitive way of applying states.

    .. rubric:: APPLYING ALL STATES CONFIGURED IN TOP.SLS (A.K.A. :ref:`HIGHSTATE <running-highstate>`)

    To apply all configured states, simply run ``state.apply``:

    .. code-block:: bash

        salt '*' state.apply

    The following additional arguments are also accepted when applying all
    states configured in top.sls:

    test
        Run states in test-only (dry-run) mode

    pillar
        Custom Pillar values, passed as a dictionary of key-value pairs

        .. code-block:: bash

            salt '*' state.apply test pillar='{"foo": "bar"}'

        .. note::
            Values passed this way will override Pillar values set via
            ``pillar_roots`` or an external Pillar source.

    exclude
        Exclude specific states from execution. Accepts a list of sls names, a
        comma-separated string of sls names, or a list of dictionaries
        containing ``sls`` or ``id`` keys. Glob-patterns may be used to match
        multiple states.

        .. code-block:: bash

            salt '*' state.apply exclude=bar,baz
            salt '*' state.apply exclude=foo*
            salt '*' state.apply exclude="[{'id': 'id_to_exclude'}, {'sls': 'sls_to_exclude'}]"

    queue : False
        Instead of failing immediately when another state run is in progress,
        queue the new state run to begin running once the other has finished.

        This option starts a new thread for each queued state run, so use this
        option sparingly.

    localconfig
        Optionally, instead of using the minion config, load minion opts from
        the file specified by this argument, and then merge them with the
        options from the minion config. This functionality allows for specific
        states to be run with their own custom minion configuration, including
        different pillars, file_roots, etc.

        .. code-block:: bash

            salt '*' state.apply localconfig=/path/to/minion.yml


    .. rubric:: APPLYING INDIVIDUAL SLS FILES (A.K.A. :py:func:`STATE.SLS <salt.modules.state.sls>`)

    To apply individual SLS files, pass them as a comma-separated list:

    .. code-block:: bash

        # Run the states configured in salt://test.sls (or salt://test/init.sls)
        salt '*' state.apply test
        # Run the states configured in salt://test.sls (or salt://test/init.sls)
        # and salt://pkgs.sls (or salt://pkgs/init.sls).
        salt '*' state.apply test,pkgs

    The following additional arguments are also accepted when applying
    individual SLS files:

    test
        Run states in test-only (dry-run) mode

    pillar
        Custom Pillar values, passed as a dictionary of key-value pairs

        .. code-block:: bash

            salt '*' state.apply test pillar='{"foo": "bar"}'

        .. note::
            Values passed this way will override Pillar values set via
            ``pillar_roots`` or an external Pillar source.

    queue : False
        Instead of failing immediately when another state run is in progress,
        queue the new state run to begin running once the other has finished.

        This option starts a new thread for each queued state run, so use this
        option sparingly.

    concurrent : False
        Execute state runs concurrently instead of serially

        .. warning::

            This flag is potentially dangerous. It is designed for use when
            multiple state runs can safely be run at the same time. Do *not*
            use this flag for performance optimization.

    saltenv
        Specify a salt fileserver environment to be used when applying states

        .. versionchanged:: 0.17.0
            Argument name changed from ``env`` to ``saltenv``

        .. versionchanged:: 2014.7.0
            If no saltenv is specified, the minion config will be checked for an
            ``environment`` parameter and if found, it will be used. If none is
            found, ``base`` will be used. In prior releases, the minion config
            was not checked and ``base`` would always be assumed when the
            saltenv was not explicitly set.

    pillarenv
        Specify a Pillar environment to be used when applying states. This
        can also be set in the minion config file using the
        :conf_minion:`pillarenv` option. When neither the
        :conf_minion:`pillarenv` minion config option nor this CLI argument is
        used, all Pillar environments will be merged together.

    localconfig
        Optionally, instead of using the minion config, load minion opts from
        the file specified by this argument, and then merge them with the
        options from the minion config. This functionality allows for specific
        states to be run with their own custom minion configuration, including
        different pillars, file_roots, etc.

        .. code-block:: bash

            salt '*' state.apply test localconfig=/path/to/minion.yml

    sync_mods
        If specified, the desired custom module types will be synced prior to
        running the SLS files:

        .. code-block:: bash

            salt '*' state.apply test sync_mods=states,modules
            salt '*' state.apply test sync_mods=all

        .. note::
            This option is ignored when no SLS files are specified, as a
            :ref:`highstate <running-highstate>` automatically syncs all custom
            module types.

        .. versionadded:: 2017.7.8,2018.3.3,Fluorine
    '''
    if mods:
        return sls(mods, **kwargs)
    return highstate(**kwargs)