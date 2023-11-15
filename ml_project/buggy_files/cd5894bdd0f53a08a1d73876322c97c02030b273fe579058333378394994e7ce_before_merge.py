def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            deregistration_delay_timeout=dict(type='int'),
            health_check_protocol=dict(choices=['http', 'https', 'tcp', 'HTTP', 'HTTPS', 'TCP']),
            health_check_port=dict(),
            health_check_path=dict(),
            health_check_interval=dict(type='int'),
            health_check_timeout=dict(type='int'),
            healthy_threshold_count=dict(type='int'),
            modify_targets=dict(default=True, type='bool'),
            name=dict(required=True),
            port=dict(type='int'),
            protocol=dict(choices=['http', 'https', 'tcp', 'HTTP', 'HTTPS', 'TCP']),
            purge_tags=dict(default=True, type='bool'),
            stickiness_enabled=dict(type='bool'),
            stickiness_type=dict(default='lb_cookie'),
            stickiness_lb_cookie_duration=dict(type='int'),
            state=dict(required=True, choices=['present', 'absent']),
            successful_response_codes=dict(),
            tags=dict(default={}, type='dict'),
            target_type=dict(default='instance', choices=['instance', 'ip']),
            targets=dict(type='list'),
            unhealthy_threshold_count=dict(type='int'),
            vpc_id=dict(),
            wait_timeout=dict(type='int'),
            wait=dict(type='bool')
        )
    )

    module = AnsibleAWSModule(argument_spec=argument_spec,
                              required_if=[['state', 'present', ['protocol', 'port', 'vpc_id']]])

    connection = module.client('elbv2')

    if module.params.get('state') == 'present':
        create_or_update_target_group(connection, module)
    else:
        delete_target_group(connection, module)