def add_advantages(policy,
                   sample_batch,
                   other_agent_batches=None,
                   episode=None):

    completed = sample_batch[SampleBatch.DONES][-1]
    if completed:
        last_r = 0.0
    else:
        last_r = policy._value(sample_batch[SampleBatch.NEXT_OBS][-1])

    return compute_advantages(
        sample_batch, last_r, policy.config["gamma"], policy.config["lambda"],
        policy.config["use_gae"], policy.config["use_critic"])