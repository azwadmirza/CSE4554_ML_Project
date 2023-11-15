def over(env='base', os_fn=None):
    '''
    Execute an overstate sequence to orchestrate the executing of states
    over a group of systems

    CLI Examples:

    .. code-block:: bash

        salt-run state.over
        salt-run state.over env=dev /root/overstate.sls
    '''
    stage_num = 0
    overstate = salt.overstate.OverState(__opts__, env, os_fn)
    for stage in overstate.stages_iter():
        if isinstance(stage, dict):
            # This is highstate data
            print('Stage execution results:')
            for key, val in stage.items():
                if '_|-' in key:
                    salt.output.display_output(
                            {'error': {key: val}},
                            'highstate',
                            opts=__opts__)
                else:
                    salt.output.display_output(
                            {key: val},
                            'highstate',
                            opts=__opts__)
        elif isinstance(stage, list):
            # This is a stage
            if stage_num == 0:
                print('Executing the following Over State:')
            else:
                print('Executed Stage:')
            salt.output.display_output(stage, 'overstatestage', opts=__opts__)
            stage_num += 1
    return overstate.over_run