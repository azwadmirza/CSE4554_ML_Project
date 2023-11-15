    def scale_sampler(
        self,
        selection: Union[List[bool], np.ndarray],
        n_samples: Optional[int] = 5000,
        n_samples_per_cell: Optional[int] = None,
        batchid: Optional[Union[List[int], np.ndarray]] = None,
        use_observed_batches: Optional[bool] = False,
        give_mean: Optional[bool] = False,
    ) -> dict:
        """
        Samples the posterior scale using the variational posterior distribution.

        Parameters
        ----------
        selection
            Mask or list of cell ids to select
        n_samples
            Number of samples in total per batch (fill either `n_samples_total`
            or `n_samples_per_cell`)
        n_samples_per_cell
            Number of time we sample from each observation per batch
            (fill either `n_samples_total` or `n_samples_per_cell`)
        batchid
            Biological batch for which to sample from.
            Default (None) sample from all batches
        use_observed_batches
            Whether normalized means are conditioned on observed
            batches or if observed batches are to be used
        give_mean
            Return mean of values


        Returns
        -------
        type
            Dictionary containing:
            `scale`
            Posterior aggregated scale samples of shape (n_samples, n_vars)
            where n_samples correspond to either:
            - n_bio_batches * n_cells * n_samples_per_cell
            or
            - n_samples_total
            `batch`
            associated batch ids

        """
        # Get overall number of desired samples and desired batches
        if batchid is None and not use_observed_batches:
            # TODO determine if we iterate over all categorical batches from train dataset
            # or just the batches in adata
            batchid = np.unique(get_from_registry(self.adata, key=_CONSTANTS.BATCH_KEY))
        if use_observed_batches:
            if batchid is not None:
                raise ValueError("Unconsistent batch policy")
            batchid = [None]
        if n_samples is None and n_samples_per_cell is None:
            n_samples = 5000
        elif n_samples_per_cell is not None and n_samples is None:
            n_samples = n_samples_per_cell * len(selection)
        if (n_samples_per_cell is not None) and (n_samples is not None):
            warnings.warn(
                "n_samples and n_samples_per_cell were provided. Ignoring n_samples_per_cell"
            )
        n_samples = int(n_samples / len(batchid))
        if n_samples == 0:
            warnings.warn(
                "very small sample size, please consider increasing `n_samples`"
            )
            n_samples = 2

        # Selection of desired cells for sampling
        if selection is None:
            raise ValueError("selections should be a list of cell subsets indices")
        selection = np.asarray(selection)
        if selection.dtype is np.dtype("bool"):
            if len(selection) < self.adata.shape[0]:
                raise ValueError("Mask must be same length as adata.")
            selection = np.asarray(np.where(selection)[0].ravel())

        # Sampling loop
        px_scales = []
        batch_ids = []
        for batch_idx in batchid:
            idx = np.random.choice(np.arange(self.adata.shape[0])[selection], n_samples)
            px_scales.append(
                self.model_fn(self.adata, indices=idx, transform_batch=batch_idx)
            )
            batch_idx = batch_idx if batch_idx is not None else np.nan
            batch_ids.append([batch_idx] * px_scales[-1].shape[0])
        px_scales = np.concatenate(px_scales)
        batch_ids = np.concatenate(batch_ids).reshape(-1)
        if px_scales.shape[0] != batch_ids.shape[0]:
            raise ValueError("sampled scales and batches have inconsistent shapes")
        if give_mean:
            px_scales = px_scales.mean(0)
        return dict(scale=px_scales, batch=batch_ids)