def _nic_profile(nic):
    '''
    Gather the nic profile from the config or apply the default.

    This is the ``default`` profile, which can be overridden in the
    configuration:

    .. code-block:: yaml

        lxc.nic:
          default:
            eth0:
              link: br0
              type: veth
    '''
    default = {'eth0': {'link': 'br0', 'type': 'veth'}}
    return __salt__['config.option']('lxc.nic', {}).get(nic, default)