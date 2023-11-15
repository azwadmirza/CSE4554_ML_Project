def main():
    argument_spec = dict(
        checkpoint_file=dict(required=False),
        rollback_to=dict(required=False),
        include_defaults=dict(default=True),
        config=dict(),
        save=dict(type='bool', default=False)
    )

    argument_spec.update(nxos_argument_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                           mutually_exclusive=[['checkpoint_file',
                                                'rollback_to']],
                           supports_check_mode=False)

    checkpoint_file = module.params['checkpoint_file']
    rollback_to = module.params['rollback_to']

    status = None
    filename = None
    changed = False

    if checkpoint_file:
        checkpoint(checkpoint_file, module)
        status = 'checkpoint file created'
    elif rollback_to:
        rollback(rollback_to, module)
        status = 'rollback executed'
    changed = True
    filename = rollback_to or checkpoint_file

    module.exit_json(changed=changed, status=status, filename=filename)