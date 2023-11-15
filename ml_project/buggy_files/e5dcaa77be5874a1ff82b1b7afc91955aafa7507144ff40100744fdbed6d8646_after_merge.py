    def __init__(self,
        emitter,
        stakeholder,
        stakeholder_config_path,
        blockchain_provider=None,
        nucypher_image=None,
        seed_network=False,
        profile=None,
        prometheus=False,
        pre_config=False,
        network=None,
        namespace=None,
        gas_strategy=None,
        action=None,
        envvars=None,
        ):

        self.emitter = emitter
        self.stakeholder = stakeholder
        self.network = network
        self.namespace = namespace or 'local-stakeholders'
        self.action = action
        self.envvars = envvars or []
        if self.envvars:
            if not all([ (len(v.split('=')) == 2) for v in self.envvars]):
                raise  ValueError("Improperly specified environment variables: --env variables must be specified in pairs as `<name>=<value>`")
            self.envvars = [v.split('=') for v in (self.envvars)]

        self.config_filename = f'{self.network}-{self.namespace}.json'

        self.created_new_nodes = False

        # the keys in this dict are used as search patterns by the anisble result collector and it will return
        # these values for each node if it happens upon them in some output
        self.output_capture = {'worker address': [], 'rest url': [], 'nucypher version': [], 'nickname': []}

        if pre_config:
            self.config = pre_config
            self.namespace_network = self.config.get('namespace')
            return

        # where we save our state data so we can remember the resources we created for future use
        self.config_path = os.path.join(self.network_config_path, self.namespace, self.config_filename)
        self.config_dir = os.path.dirname(self.config_path)

        if os.path.exists(self.config_path):
            self.config = json.load(open(self.config_path))
            self.namespace_network = self.config['namespace']
        else:
            self.namespace_network = f'{self.network}-{self.namespace}-{maya.now().date.isoformat()}'
            self.emitter.echo(f"Configuring Cloud Deployer with namespace: '{self.namespace_network}'")
            time.sleep(3)

            self.config = {
                "namespace": self.namespace_network,
                "keyringpassword": b64encode(os.urandom(64)).decode('utf-8'),
                "ethpassword": b64encode(os.urandom(64)).decode('utf-8'),
            }

        # configure provider specific attributes
        self._configure_provider_params(profile)

        # if certain config options have been specified with this invocation,
        # save these to update host specific variables before deployment
        # to allow for individual host config differentiation
        self.host_level_overrides = {
            'blockchain_provider': blockchain_provider,
            'nucypher_image': nucypher_image,
            'gas_strategy': f'--gas-strategy {gas_strategy}' if gas_strategy else '',
        }

        self.config['blockchain_provider'] = blockchain_provider or self.config.get('blockchain_provider') or f'/root/.local/share/geth/.ethereum/{self.chain_name}/geth.ipc' # the default for nodes that run their own geth container
        self.config['nucypher_image'] = nucypher_image or self.config.get('nucypher_image') or 'nucypher/nucypher:latest'
        self.config['gas_strategy'] = f'--gas-strategy {gas_strategy}' if gas_strategy else self.config.get('gas-strategy', '')

        self.config['seed_network'] = seed_network if seed_network is not None else self.config.get('seed_network')
        if not self.config['seed_network']:
            self.config.pop('seed_node', None)
        self.nodes_are_decentralized = 'geth.ipc' in self.config['blockchain_provider']
        self.config['stakeholder_config_file'] = stakeholder_config_path
        self.config['use-prometheus'] = prometheus

        # add instance key as host_nickname for use in inventory
        if self.config.get('instances'):
            for k, v in self.config['instances'].items():
                self.config['instances'][k]['host_nickname'] = k

        self._write_config()