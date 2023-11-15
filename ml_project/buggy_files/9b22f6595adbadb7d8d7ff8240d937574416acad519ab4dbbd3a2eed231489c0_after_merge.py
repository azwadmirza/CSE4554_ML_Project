    def __init__(self, registry, config, policy_params, env_creator, noise,
                 min_task_runtime=0.2):
        self.min_task_runtime = min_task_runtime
        self.config = config
        self.policy_params = policy_params
        self.noise = SharedNoiseTable(noise)

        self.env = env_creator(config["env_config"])
        from ray.rllib import models
        self.preprocessor = models.ModelCatalog.get_preprocessor(
            registry, self.env)

        self.sess = utils.make_session(single_threaded=True)
        self.policy = policies.GenericPolicy(
            registry, self.sess, self.env.action_space, self.preprocessor,
            config["observation_filter"], **policy_params)