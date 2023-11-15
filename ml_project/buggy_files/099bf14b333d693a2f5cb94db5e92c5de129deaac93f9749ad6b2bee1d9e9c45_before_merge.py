def get_agent_class(alg):
    """Returns the class of an known agent given its name."""

    if alg == "PPO":
        from ray.rllib import ppo
        return ppo.PPOAgent
    elif alg == "ES":
        from ray.rllib import es
        return es.ESAgent
    elif alg == "DQN":
        from ray.rllib import dqn
        return dqn.DQNAgent
    elif alg == "APEX":
        from ray.rllib import dqn
        return dqn.ApexAgent
    elif alg == "A3C":
        from ray.rllib import a3c
        return a3c.A3CAgent
    elif alg == "BC":
        from ray.rllib import bc
        return bc.BCAgent
    elif alg == "PG":
        from ray.rllib import pg
        return pg.PGAgent
    elif alg == "script":
        from ray.tune import script_runner
        return script_runner.ScriptRunner
    elif alg == "__fake":
        return _MockAgent
    elif alg == "__sigmoid_fake_data":
        return _SigmoidFakeData
    elif alg == "__parameter_tuning":
        return _ParameterTuningAgent
    else:
        raise Exception(
            ("Unknown algorithm {}.").format(alg))