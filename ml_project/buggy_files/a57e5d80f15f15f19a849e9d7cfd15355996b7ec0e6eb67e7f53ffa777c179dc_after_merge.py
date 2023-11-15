        def postprocess_trajectory(self,
                                   sample_batch,
                                   other_agent_batches=None,
                                   episode=None):
            if not postprocess_fn:
                return sample_batch

            # Do all post-processing always with no_grad().
            # Not using this here will introduce a memory leak (issue #6962).
            with torch.no_grad():
                return postprocess_fn(
                    self, convert_to_non_torch_type(sample_batch),
                    convert_to_non_torch_type(other_agent_batches), episode)