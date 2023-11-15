def main():

    argument_spec = rabbitmq_argument_spec()
    argument_spec.update(
        dict(
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            name=dict(required=True, aliases=["src", "source"], type='str'),
            destination=dict(required=True, aliases=["dst", "dest"], type='str'),
            destination_type=dict(required=True, aliases=["type", "dest_type"], choices=["queue", "exchange"],
                                  type='str'),
            routing_key=dict(default='#', type='str'),
            arguments=dict(default=dict(), type='dict')
        )
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    if not HAS_REQUESTS:
        module.fail_json(msg="requests library is required for this module. To install, use `pip install requests`")

    RabbitMqBinding(module).run()