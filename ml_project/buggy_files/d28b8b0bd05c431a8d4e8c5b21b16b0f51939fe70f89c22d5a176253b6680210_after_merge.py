def get_filter_config(platform,
                      filter_name,
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
                      revision_date_format='%Y/%m/%d'):
    '''
    Return the configuration of a policy filter.

    platform
        The name of the Capirca platform.

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

    revision_id
        Add a comment in the filter config having the description for the changes applied.

    revision_no
        The revision count.

    revision_date: ``True``
        Boolean flag: display the date when the filter configuration was generated. Default: ``True``.

    revision_date_format: ``%Y/%m/%d``
        The date format to be used when generating the perforce data. Default: ``%Y/%m/%d`` (<year>/<month>/<day>).

    CLI Example:

    .. code-block:: bash

        salt '*' capirca.get_filter_config ciscoxr my-filter pillar_key=netacl

    Output Example:

    .. code-block:: text

        ! $Id:$
        ! $Date:$
        ! $Revision:$
        no ipv4 access-list my-filter
        ipv4 access-list my-filter
         remark $Id:$
         remark my-term
         deny ipv4 any eq 1234 any
         deny ipv4 any eq 1235 any
         remark my-other-term
         permit tcp any range 5678 5680 any
        exit

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
    if merge_pillar and not only_lower_merge:
        filter_pillar_key = ':'.join((pillar_key, filter_name))
        filter_pillar_cfg = _get_pillar_cfg(filter_pillar_key)
        filter_options = filter_options or filter_pillar_cfg.pop('options', None)
        terms = _merge_dict(terms, filter_pillar_cfg)
        # merge the passed variable with the pillar data
        # any filter term not defined here, will be appended from the pillar
        # new terms won't be removed
    filters = {
        filter_name: {
            'options': _make_it_list({}, filter_name, filter_options)
        }
    }
    filters[filter_name].update(terms)
    return get_policy_config(platform,
                             filters=filters,
                             pillar_key=pillar_key,
                             pillarenv=pillarenv,
                             saltenv=saltenv,
                             merge_pillar=merge_pillar,
                             only_lower_merge=True,
                             revision_id=revision_id,
                             revision_no=revision_no,
                             revision_date=revision_date,
                             revision_date_format=revision_date_format)