def create_or_update_elb_listeners(connection, module, elb):
    """Create or update ELB listeners. Return true if changed, else false"""

    listener_changed = False
    # Ensure listeners are using Target Group ARN not name
    listeners = ensure_listeners_default_action_has_arn(connection, module, module.params.get("listeners"))
    purge_listeners = module.params.get("purge_listeners")

    # Does the ELB have any listeners exist?
    current_listeners = get_elb_listeners(connection, module, elb['LoadBalancerArn'])

    listeners_to_add, listeners_to_modify, listeners_to_delete = compare_listeners(connection, module, current_listeners, deepcopy(listeners), purge_listeners)

    # Add listeners
    for listener_to_add in listeners_to_add:
        try:
            listener_to_add['LoadBalancerArn'] = elb['LoadBalancerArn']
            connection.create_listener(**listener_to_add)
            listener_changed = True
        except ClientError as e:
            module.fail_json(msg=e.message, exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))

    # Modify listeners
    for listener_to_modify in listeners_to_modify:
        try:
            connection.modify_listener(**listener_to_modify)
            listener_changed = True
        except ClientError as e:
            module.fail_json(msg=e.message, exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))

    # Delete listeners
    for listener_to_delete in listeners_to_delete:
        try:
            connection.delete_listener(ListenerArn=listener_to_delete)
            listener_changed = True
        except ClientError as e:
            module.fail_json(msg=e.message, exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))

    # For each listener, check rules
    for listener in listeners:
        if 'Rules' in listener:
            # Ensure rules are using Target Group ARN not name
            listener['Rules'] = ensure_rules_action_has_arn(connection, module, listener['Rules'])
            rules_to_add, rules_to_modify, rules_to_delete = compare_rules(connection, module, current_listeners, listener)

            # Get listener based on port so we can use ARN
            looked_up_listener = get_listener(connection, module, elb['LoadBalancerArn'], listener['Port'])

            # Add rules
            for rule in rules_to_add:
                try:
                    rule['ListenerArn'] = looked_up_listener['ListenerArn']
                    rule['Priority'] = int(rule['Priority'])
                    connection.create_rule(**rule)
                    listener_changed = True
                except ClientError as e:
                    module.fail_json(msg=e.message, exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))

            # Modify rules
            for rule in rules_to_modify:
                try:
                    del rule['Priority']
                    connection.modify_rule(**rule)
                    listener_changed = True
                except ClientError as e:
                    module.fail_json(msg=e.message, exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))

            # Delete rules
            for rule in rules_to_delete:
                try:
                    connection.delete_rule(RuleArn=rule)
                    listener_changed = True
                except ClientError as e:
                    module.fail_json(msg=e.message, exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))

    return listener_changed