    def _init(self):
        policy_params = {
            "action_noise_std": 0.01
        }

        env = self.env_creator(self.config["env_config"])
        preprocessor = ModelCatalog.get_preprocessor(self.registry, env)

        self.sess = utils.make_session(single_threaded=False)
        self.policy = policies.GenericPolicy(
            self.registry, self.sess, env.action_space, preprocessor,
            self.config["observation_filter"], **policy_params)
        self.optimizer = optimizers.Adam(self.policy, self.config["stepsize"])

        # Create the shared noise table.
        print("Creating shared noise table.")
        noise_id = create_shared_noise.remote(self.config["noise_size"])
        self.noise = SharedNoiseTable(ray.get(noise_id))

        # Create the actors.
        print("Creating actors.")
        self.workers = [
            Worker.remote(
                self.registry, self.config, policy_params, self.env_creator,
                noise_id)
            for _ in range(self.config["num_workers"])]

        self.episodes_so_far = 0
        self.timesteps_so_far = 0
        self.tstart = time.time()