    def __init__(self):

        self._args = self._parse_cli_args()

        try:
            rm = AzureRM(self._args)
        except Exception as e:
            sys.exit("{0}".format(str(e)))

        self._compute_client = rm.compute_client
        self._network_client = rm.network_client
        self._resource_client = rm.rm_client
        self._security_groups = None

        self.resource_groups = []
        self.tags = None
        self.locations = None
        self.replace_dash_in_groups = False
        self.group_by_resource_group = True
        self.group_by_location = True
        self.group_by_security_group = True
        self.group_by_tag = True
        self.include_powerstate = True
        self.use_private_ip = False

        self._inventory = dict(
            _meta=dict(
                hostvars=dict()
            ),
            azure=[]
        )

        self._get_settings()

        if self._args.resource_groups:
            self.resource_groups = self._args.resource_groups.split(',')

        if self._args.tags:
            self.tags = self._args.tags.split(',')

        if self._args.locations:
            self.locations = self._args.locations.split(',')

        if self._args.no_powerstate:
            self.include_powerstate = False

        self.get_inventory()
        print(self._json_format_dict(pretty=self._args.pretty))
        sys.exit(0)