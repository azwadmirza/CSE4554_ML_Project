    def __init__(self):
        """
            Initialize the Ontap IfGrp class
        """
        self.argument_spec = netapp_utils.na_ontap_host_argument_spec()
        self.argument_spec.update(dict(
            state=dict(required=False, choices=['present', 'absent'], default='present'),
            distribution_function=dict(required=False, type='str', choices=['mac', 'ip', 'sequential', 'port']),
            name=dict(required=True, type='str'),
            mode=dict(required=False, type='str'),
            node=dict(required=True, type='str'),
            ports=dict(required=False, type='list', aliases=["port"]),
        ))

        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            required_if=[
                ('state', 'present', ['distribution_function', 'mode'])
            ],
            supports_check_mode=True
        )

        # set up variables
        self.na_helper = NetAppModule()
        self.parameters = self.na_helper.set_parameters(self.module.params)

        if HAS_NETAPP_LIB is False:
            self.module.fail_json(msg="the python NetApp-Lib module is required")
        else:
            self.server = netapp_utils.setup_na_ontap_zapi(module=self.module)
        return