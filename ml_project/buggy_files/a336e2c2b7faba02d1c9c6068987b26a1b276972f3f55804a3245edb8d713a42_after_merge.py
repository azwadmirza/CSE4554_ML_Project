def get_policy_class(config):
    if config["framework"] == "torch":
        if config["vtrace"]:
            from ray.rllib.agents.impala.vtrace_torch_policy import \
                VTraceTorchPolicy
            return VTraceTorchPolicy
        else:
            from ray.rllib.agents.a3c.a3c_torch_policy import \
                A3CTorchPolicy
            return A3CTorchPolicy
    else:
        if config["vtrace"]:
            return VTraceTFPolicy
        else:
            from ray.rllib.agents.a3c.a3c_tf_policy import A3CTFPolicy
            return A3CTFPolicy