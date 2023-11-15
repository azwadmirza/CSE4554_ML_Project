    def fix_optimizer_models_list(self):
        """
        WORKAROUND: Since skopt is not actively supported, this resolves problems with skopt
        memory usage, see also: https://github.com/scikit-optimize/scikit-optimize/pull/746

        This may cease working when skopt updates if implementation of this intrinsic
        part changes.
        """
        n = len(self.opt.models) - SKOPT_MODELS_MAX_NUM
        # Keep no more than 2*SKOPT_MODELS_MAX_NUM models in the skopt models list,
        # remove the old ones. These are actually of no use, the current model
        # from the estimator is the only one used in the skopt optimizer.
        # Freqtrade code also does not inspect details of the models.
        if n >= SKOPT_MODELS_MAX_NUM:
            logger.debug(f"Fixing skopt models list, removing {n} old items...")
            del self.opt.models[0:n]