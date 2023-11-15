def postprocess_ppo_gae(
        policy: Policy,
        sample_batch: SampleBatch,
        other_agent_batches: Optional[Dict[AgentID, SampleBatch]] = None,
        episode: Optional[MultiAgentEpisode] = None) -> SampleBatch:

    # Stub serving backward compatibility.
    deprecation_warning(
        old="rllib.agents.ppo.ppo_tf_policy.postprocess_ppo_gae",
        new="rllib.evaluation.postprocessing.compute_gae_for_sample_batch",
        error=False)

    return compute_gae_for_sample_batch(policy, sample_batch,
                                        other_agent_batches, episode)