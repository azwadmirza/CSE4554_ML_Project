    def __call__(self, engine: Engine) -> None:
        """
        This method assumes self.batch_transform will extract metadata from the input batch.

        Args:
            engine: Ignite Engine, it can be a trainer, validator or evaluator.
        """
        _meta_data = self.batch_transform(engine.state.batch)
        if Key.FILENAME_OR_OBJ in _meta_data:
            # all gather filenames across ranks, only filenames are necessary
            _meta_data = {Key.FILENAME_OR_OBJ: string_list_all_gather(_meta_data[Key.FILENAME_OR_OBJ])}
        # all gather predictions across ranks
        _engine_output = evenly_divisible_all_gather(self.output_transform(engine.state.output))

        if self._expected_rank:
            self.saver.save_batch(_engine_output, _meta_data)