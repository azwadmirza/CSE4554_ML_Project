def main():
    """The main function."""
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(aliases=['pkg'], type='list'),
            state=dict(
                default='installed',
                choices=[
                    'absent', 'present', 'installed', 'removed', 'latest']),
            enablerepo=dict(type='list', default=[]),
            disablerepo=dict(type='list', default=[]),
            list=dict(),
            conf_file=dict(default=None, type='path'),
            disable_gpg_check=dict(default=False, type='bool'),
        ),
        required_one_of=[['name', 'list']],
        mutually_exclusive=[['name', 'list']],
        supports_check_mode=True)
    params = module.params

    _fail_if_no_dnf(module)
    if params['list']:
        base = _base(
            module, params['conf_file'], params['disable_gpg_check'],
            params['disablerepo'], params['enablerepo'])
        list_items(module, base, params['list'])
    else:
        # Note: base takes a long time to run so we want to check for failure
        # before running it.
        if not util.am_i_root():
            module.fail_json(msg="This command has to be run under the root user.")
        base = _base(
            module, params['conf_file'], params['disable_gpg_check'],
            params['disablerepo'], params['enablerepo'])

        ensure(module, base, params['state'], params['name'])