        def _identify_local_rank(self):

            if "SLURM_JOBID" in os.environ:
                os.environ["LOCAL_RANK"] = os.environ["SLURM_LOCALID"]

            if "LOCAL_RANK" in os.environ:
                self._local_rank = int(os.environ["LOCAL_RANK"])
            elif self._ext_local_rank is not None:
                self._local_rank = self._ext_local_rank
            else:
                warnings.warn(
                    "Local rank information for native distributed setting will be initialized using "
                    "heuristic approach based on hostname which can be different of real setup. Please, "
                    "either set `os.environ['LOCAL_RANK']` "
                    "or use `idist.set_local_rank(local_rank)` with correct local rank index."
                )
                # use socket gethostname heuristic to determine number of nodes => local rank
                self._local_rank = self._compute_local_rank_via_hostname()