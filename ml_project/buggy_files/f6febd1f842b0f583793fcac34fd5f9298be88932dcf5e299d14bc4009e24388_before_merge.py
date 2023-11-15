    def _generate_compose_file(self, command, additional_volumes=None, additional_env_vars=None):
        """Writes a config file describing a training/hosting  environment.

        This method generates a docker compose configuration file, it has an entry for each container
        that will be created (based on self.hosts). it calls
        :meth:~sagemaker.local_session.SageMakerContainer._create_docker_host to generate the config
        for each individual container.

        Args:
            command (str): either 'train' or 'serve'
            additional_volumes (list): a list of volumes that will be mapped to the containers
            additional_env_vars (dict): a dictionary with additional environment variables to be
                passed on to the containers.

        Returns: (dict) A dictionary representation of the configuration that was written.

        """
        boto_session = self.sagemaker_session.boto_session
        additional_env_vars = additional_env_vars or []
        additional_volumes = additional_volumes or {}
        environment = []
        optml_dirs = set()

        aws_creds = _aws_credentials(boto_session)
        if aws_creds is not None:
            environment.extend(aws_creds)

        additional_env_var_list = ['{}={}'.format(k, v) for k, v in additional_env_vars.items()]
        environment.extend(additional_env_var_list)

        if command == 'train':
            optml_dirs = {'output', 'output/data', 'input'}

        services = {
            h: self._create_docker_host(h, environment, optml_dirs,
                                        command, additional_volumes) for h in self.hosts
        }

        content = {
            # Use version 2.3 as a minimum so that we can specify the runtime
            'version': '2.3',
            'services': services,
            'networks': {
                'sagemaker-local': {'name': 'sagemaker-local'}
            }

        }

        docker_compose_path = os.path.join(self.container_root, DOCKER_COMPOSE_FILENAME)
        yaml_content = yaml.dump(content, default_flow_style=False)
        logger.info('docker compose file: \n{}'.format(yaml_content))
        with open(docker_compose_path, 'w') as f:
            f.write(yaml_content)

        return content