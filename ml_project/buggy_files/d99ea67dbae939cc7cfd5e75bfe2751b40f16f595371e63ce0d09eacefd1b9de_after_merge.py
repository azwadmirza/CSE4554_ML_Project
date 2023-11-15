def load_filter_config(filter_name,
                       filter_options=None,
                       terms=None,
                       pillar_key='acl',
                       pillarenv=None,
                       saltenv=None,
                       merge_pillar=True,
                       only_lower_merge=False,
                       revision_id=None,
                       revision_no=None,
                       revision_date=True,
                       revision_date_format='%Y/%m/%d',
                       test=False,
                       commit=True,
                       debug=False,
                       **kwargs):  # pylint: disable=unused-argument
    '''
    Generate and load the configuration of a policy filter.

    filter_name
        The name of the policy filter.

    filter_options
        Additional filter options. These options are platform-specific.
        See the complete list of options_.

        .. _options: https://github.com/google/capirca/wiki/Policy-format#header-section

    terms
        Dictionary of terms for this policy filter.
        If not specified or empty, will try to load the configuration from the pillar,
        unless ``merge_pillar`` is set as ``False``.

    pillar_key: ``acl``
        The key in the pillar containing the default attributes values. Default: ``acl``.

    pillarenv
        Query the master to generate fresh pillar data on the fly,
        specifically from the requested pillar environment.

    saltenv
        Included only for compatibility with
        :conf_minion:`pillarenv_from_saltenv`, and is otherwise ignored.

    merge_pillar: ``True``
        Merge the CLI variables with the pillar. Default: ``True``

    only_lower_merge: ``False``
        Specify if it should merge only the terms fields. Otherwise it will try
        to merge also filters fields. Default: ``False``.
        This option requires ``merge_pillar``, otherwise it is ignored.

    revision_id
        Add a comment in the filter config having the description for the changes applied.

    revision_no
        The revision count.

    revision_date: ``True``
        Boolean flag: display the date when the filter configuration was generated. Default: ``True``.

    revision_date_format: ``%Y/%m/%d``
        The date format to be used when generating the perforce data. Default: ``%Y/%m/%d`` (<year>/<month>/<day>).

    test: ``False``
        Dry run? If set as ``True``, will apply the config, discard and return the changes.
        Default: ``False`` and will commit the changes on the device.

    commit: ``True``
        Commit? Default: ``True``.

    debug: ``False``
        Debug mode. Will insert a new key under the output dictionary,
        as ``loaded_config`` contaning the raw configuration loaded on the device.

    The output is a dictionary having the same form as :mod:`net.load_config <salt.modules.napalm_network.load_config>`.
    CLI Example:

    .. code-block:: bash

        salt 'edge01.bjm01' netacl.load_filter_config my-filter pillar_key=netacl debug=True

    Output Example:

    .. code-block:: yaml

        edge01.bjm01:
            ----------
            already_configured:
                False
            comment:
            diff:
                [edit firewall]
                +    family inet {
                +        /*
                +         ** $Id:$
                +         ** $Date:$
                +         ** $Revision:$
                +         **
                +         */
                +        filter my-filter {
                +            interface-specific;
                +            term my-term {
                +                from {
                +                    source-port [ 1234 1235 ];
                +                }
                +                then {
                +                    reject;
                +                }
                +            }
                +            term my-other-term {
                +                from {
                +                    protocol tcp;
                +                    source-port 5678-5680;
                +                }
                +                then accept;
                +            }
                +        }
                +    }
            loaded_config:
                firewall {
                    family inet {
                        replace:
                        /*
                        ** $Id:$
                        ** $Date:$
                        ** $Revision:$
                        **
                        */
                        filter my-filter {
                            interface-specific;
                            term my-term {
                                from {
                                    source-port [ 1234 1235 ];
                                }
                                then {
                                    reject;
                                }
                            }
                            term my-other-term {
                                from {
                                    protocol tcp;
                                    source-port 5678-5680;
                                }
                                then accept;
                            }
                        }
                    }
                }
            result:
                True

    The filter configuration has been loaded from the pillar, having the following structure:

    .. code-block:: yaml

        netacl:
          my-filter:
            my-term:
              source_port: [1234, 1235]
              action: reject
            my-other-term:
              source_port:
                - [5678, 5680]
              protocol: tcp
              action: accept
    '''
    if not filter_options:
        filter_options = []
    if not terms:
        terms = {}
    platform = _get_capirca_platform()
    filter_config = __salt__['capirca.get_filter_config'](platform,
                                                          filter_name,
                                                          terms=terms,
                                                          filter_options=filter_options,
                                                          pillar_key=pillar_key,
                                                          pillarenv=pillarenv,
                                                          saltenv=saltenv,
                                                          merge_pillar=merge_pillar,
                                                          only_lower_merge=only_lower_merge,
                                                          revision_id=revision_id,
                                                          revision_no=revision_no,
                                                          revision_date=revision_date,
                                                          revision_date_format=revision_date_format)
    return __salt__['net.load_config'](text=filter_config,
                                       test=test,
                                       commit=commit,
                                       debug=debug,
                                       inherit_napalm_device=napalm_device)  # pylint: disable=undefined-variable