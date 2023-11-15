def load_policy_config(filters=None,
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
                       debug=False):
    '''
    Generate and load the configuration of the whole policy.

    filters
        Dictionary of filters for this policy.
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
        Merge the CLI variables with the pillar. Default: ``True``.

    only_lower_merge: ``False``
        Specify if it should merge only the filters and terms fields. Otherwise it will try
        to merge everything at the policy level. Default: ``False``.
        This option requires ``merge_pillar``, otherwise it is ignored.

    revision_id
        Add a comment in the policy config having the description for the changes applied.

    revision_no
        The revision count.

    revision_date: ``True``
        Boolean flag: display the date when the policy configuration was generated. Default: ``True``.

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

        salt 'edge01.flw01' netacl.load_policy_config debug=True

    Output Example:

    .. code-block:: yaml

        edge01.flw01:
            ----------
            already_configured:
                False
            comment:
            diff:
                ---
                +++
                @@ -1228,9 +1228,24 @@
                 !
                +ipv4 access-list my-filter
                + 10 remark $Id:$
                + 20 remark my-term
                + 30 deny tcp host 1.2.3.4 eq 1234 any
                + 40 deny udp host 1.2.3.4 eq 1234 any
                + 50 deny tcp host 1.2.3.4 eq 1235 any
                + 60 deny udp host 1.2.3.4 eq 1235 any
                + 70 remark my-other-term
                + 80 permit tcp any range 5678 5680 any
                +!
                +!
                +ipv4 access-list block-icmp
                + 10 remark $Id:$
                + 20 remark first-term
                + 30 deny icmp any any
                 !
            loaded_config:
                ! $Id:$
                ! $Date:$
                ! $Revision:$
                no ipv4 access-list block-icmp
                ipv4 access-list block-icmp
                 remark $Id:$
                 remark first-term
                 deny icmp any any
                exit
                no ipv4 access-list my-filter
                ipv4 access-list my-filter
                 remark $Id:$
                 remark my-term
                 deny tcp host 1.2.3.4 eq 1234 any
                 deny udp host 1.2.3.4 eq 1234 any
                 deny tcp host 1.2.3.4 eq 1235 any
                 deny udp host 1.2.3.4 eq 1235 any
                 remark my-other-term
                 permit tcp any range 5678 5680 any
                exit
            result:
                True

    The policy configuration has been loaded from the pillar, having the following structure:

    .. code-block:: yaml

        acl:
          my-filter:
            my-term:
              source_port: [1234, 1235]
              protocol:
                - tcp
                - udp
              source_address: 1.2.3.4
              action: reject
            my-other-term:
              source_port:
                - [5678, 5680]
              protocol: tcp
              action: accept
          block-icmp:
            first-term:
              protocol:
                - icmp
              action: reject
    '''
    if not filters:
        filters = {}
    platform = _get_capirca_platform()
    policy_config = __salt__['capirca.get_policy_config'](platform,
                                                          filters=filters,
                                                          pillar_key=pillar_key,
                                                          pillarenv=pillarenv,
                                                          saltenv=saltenv,
                                                          merge_pillar=merge_pillar,
                                                          only_lower_merge=only_lower_merge,
                                                          revision_id=revision_id,
                                                          revision_no=revision_no,
                                                          revision_date=revision_date,
                                                          revision_date_format=revision_date_format)
    return __salt__['net.load_config'](text=policy_config,
                                       test=test,
                                       commit=commit,
                                       debug=debug,
                                       inherit_napalm_device=napalm_device)  # pylint: disable=undefined-variable