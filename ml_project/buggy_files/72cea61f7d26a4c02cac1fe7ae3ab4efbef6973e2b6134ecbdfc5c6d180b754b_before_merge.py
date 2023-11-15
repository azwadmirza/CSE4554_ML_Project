    def reproduce_one(self, queue=False, **kwargs):
        """Reproduce and checkout a single experiment."""
        checkpoint = kwargs.get("checkpoint", False)
        stash_rev = self.new(**kwargs)
        if queue:
            logger.info(
                "Queued experiment '%s' for future execution.", stash_rev[:7]
            )
            return [stash_rev]
        results = self.reproduce(
            [stash_rev], keep_stash=False, checkpoint=checkpoint
        )
        exp_rev = first(results)
        if exp_rev is not None:
            self.checkout_exp(exp_rev, allow_missing=checkpoint)
        return results