def postprocess_advantages(policy,
                           sample_batch,
                           other_agent_batches=None,
                           episode=None):

    # Stub serving backward compatibility.
    deprecation_warning(
        old="rllib.agents.a3c.a3c_tf_policy.postprocess_advantages",
        new="rllib.evaluation.postprocessing.compute_gae_for_sample_batch",
        error=False)

    return compute_gae_for_sample_batch(policy, sample_batch,
                                        other_agent_batches, episode)