def compare_rules(connection, module, current_listeners, listener):

    """
    Compare rules and return rules to add, rules to modify and rules to remove
    Rules are compared based on priority

    :param connection: ELBv2 boto3 connection
    :param module: Ansible module object
    :param current_listeners: list of listeners currently associated with the ELB
    :param listener: dict object of a listener passed by the user
    :return:
    """

    # Run through listeners looking for a match (by port) to get the ARN
    for current_listener in current_listeners:
        if current_listener['Port'] == listener['Port']:
            listener['ListenerArn'] = current_listener['ListenerArn']
            break

    # If the listener exists (i.e. has an ARN) get rules for the listener
    if 'ListenerArn' in listener:
        current_rules = get_listener_rules(connection, module, listener['ListenerArn'])
    else:
        current_rules = []

    rules_to_modify = []
    rules_to_delete = []

    for current_rule in current_rules:
        current_rule_passed_to_module = False
        for new_rule in listener['Rules'][:]:
            if current_rule['Priority'] == new_rule['Priority']:
                current_rule_passed_to_module = True
                # Remove what we match so that what is left can be marked as 'to be added'
                listener['Rules'].remove(new_rule)
                modified_rule = compare_rule(current_rule, new_rule)
                if modified_rule:
                    modified_rule['Priority'] = int(current_rule['Priority'])
                    modified_rule['RuleArn'] = current_rule['RuleArn']
                    modified_rule['Actions'] = new_rule['Actions']
                    modified_rule['Conditions'] = new_rule['Conditions']
                    rules_to_modify.append(modified_rule)
                break

        # If the current rule was not matched against passed rules, mark for removal
        if not current_rule_passed_to_module and not current_rule['IsDefault']:
            rules_to_delete.append(current_rule['RuleArn'])

    rules_to_add = listener['Rules']

    return rules_to_add, rules_to_modify, rules_to_delete