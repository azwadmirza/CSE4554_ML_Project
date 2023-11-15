def configured(name,
               data,
               **kwargs):
    '''
    Configure the network device, given the input data strucuted
    according to the YANG models.

    .. note::
        The main difference between this function and ``managed``
        is that the later generates and loads the configuration
        only when there are differences between the existing
        configuration on the device and the expected
        configuration. Depending on the platform and hardware
        capabilities, one could be more optimal than the other.
        Additionally, the output of the ``managed`` is different,
        in such a way that the ``pchange`` field in the output
        contains structured data, rather than text.

    data
        YANG structured data.

    models
         A list of models to be used when generating the config.

    profiles: ``None``
        Use certain profiles to generate the config.
        If not specified, will use the platform default profile(s).

    test: ``False``
        Dry run? If set as ``True``, will apply the config, discard
        and return the changes. Default: ``False`` and will commit
        the changes on the device.

    commit: ``True``
        Commit? Default: ``True``.

    debug: ``False``
        Debug mode. Will insert a new key under the output dictionary,
        as ``loaded_config`` containing the raw configuration loaded on the device.

    replace: ``False``
        Should replace the config with the new generate one?

    State SLS example:

    .. code-block:: jinja

        {%- set expected_config =  pillar.get('openconfig_interfaces_cfg') -%}
        interfaces_config:
          napalm_yang.configured:
            - data: {{ expected_config | json }}
            - models:
              - models.openconfig_interfaces
            - debug: true

    Pillar example:

    .. code-block:: yaml

        openconfig_interfaces_cfg:
          _kwargs:
            filter: true
          interfaces:
            interface:
              Et1:
                config:
                  mtu: 9000
              Et2:
                config:
                  description: "description example"
    '''
    models = kwargs.get('models', None)
    if isinstance(models, tuple) and isinstance(models[0], list):
        models = models[0]
    ret = salt.utils.napalm.default_ret(name)
    test = kwargs.get('test', False) or __opts__.get('test', False)
    debug = kwargs.get('debug', False) or __opts__.get('debug', False)
    commit = kwargs.get('commit', True) or __opts__.get('commit', True)
    replace = kwargs.get('replace', False) or __opts__.get('replace', False)
    profiles = kwargs.get('profiles', [])
    if '_kwargs' in data:
        data.pop('_kwargs')
    loaded_changes = __salt__['napalm_yang.load_config'](data,
                                                         *models,
                                                         profiles=profiles,
                                                         test=test,
                                                         debug=debug,
                                                         commit=commit,
                                                         replace=replace)
    return salt.utils.napalm.loaded_ret(ret, loaded_changes, test, debug)