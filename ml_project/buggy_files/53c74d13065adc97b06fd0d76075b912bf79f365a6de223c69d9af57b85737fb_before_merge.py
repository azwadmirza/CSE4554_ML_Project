    def _reset_eval_dataloader(
            self,
            model: LightningModule,
            mode: str
    ) -> Tuple[List[Union[int, float]], List[DataLoader]]:
        """Generic method to reset a dataloader for evaluation.

        Args:
            model: The current `LightningModule`
            mode: Either `'val'` or `'test'`

        Returns:
            Tuple (num_batches, dataloaders)
        """
        # use the training loader as val and test when overfitting
        if self.overfit_batches > 0:
            dataloaders = self.request_dataloader(getattr(model, 'train_dataloader'))
        else:
            dataloaders = self.request_dataloader(getattr(model, f'{mode}_dataloader'))

        if not isinstance(dataloaders, list):
            dataloaders = [dataloaders]

        for loader_i in range(len(dataloaders)):
            loader = dataloaders[loader_i]

            # shuffling in val and test set is bad practice
            if mode in ('val', 'test') and hasattr(loader, 'sampler') and isinstance(loader.sampler, RandomSampler):

                # when overfitting, the dataloader should not have sampler
                if self.overfit_batches > 0:
                    rank_zero_warn('You requested to overfit but enabled training dataloader shuffling.'
                                   ' We are turning it off for you.')
                    dataloaders[loader_i] = self.replace_sampler(loader, SequentialSampler(loader.dataset))

                else:
                    rank_zero_warn(f'Your {mode}_dataloader has `shuffle=True`, it is best practice to turn'
                                   ' this off for validation and test dataloaders.')

        if any([dl is None for dl in dataloaders]):
            rank_zero_warn("One of given dataloaders is None and it will be skipped.")

        # add samplers
        dataloaders = [self.auto_add_sampler(dl, train=False) for dl in dataloaders if dl is not None]

        loader_num_batches = []

        # determine number of batches
        # datasets could be none, 1 or 2+
        if len(dataloaders) != 0:
            for i, dataloader in enumerate(dataloaders):
                try:
                    num_batches = len(dataloader)
                except (TypeError, NotImplementedError):
                    num_batches = float('inf')

                self._worker_check(dataloader, f'{mode} dataloader {i}')

                # percent or num_steps
                limit_eval_batches = getattr(self, f'limit_{mode}_batches')

                if num_batches != float('inf'):
                    self._check_batch_limits(f'limit_{mode}_batches')

                    # limit num batches either as a percent or num steps
                    if isinstance(limit_eval_batches, float):
                        num_batches = int(num_batches * limit_eval_batches)
                    else:
                        num_batches = limit_eval_batches

                elif limit_eval_batches not in (0.0, 1.0):
                    raise MisconfigurationException(
                        'When using an infinite DataLoader (e.g. with an IterableDataset'
                        f' or when DataLoader does not implement `__len__`) for `limit_{mode}_batches`,'
                        f' `Trainer(limit_{mode}_batches)` must be `0.0` or `1.0`.')

                if num_batches == 0 and limit_eval_batches > 0.0 and isinstance(limit_eval_batches, float):
                    min_pct = 1.0 / len(dataloader)
                    raise MisconfigurationException(
                        f'you requested to check {limit_eval_batches} of the {mode} dataloader but'
                        f' {limit_eval_batches}*{num_batches} = 0. Please increase the limit_{mode}_batches.'
                        f' Try at least limit_{mode}_batches={min_pct}'
                    )

                loader_num_batches.append(num_batches)

        return loader_num_batches, dataloaders