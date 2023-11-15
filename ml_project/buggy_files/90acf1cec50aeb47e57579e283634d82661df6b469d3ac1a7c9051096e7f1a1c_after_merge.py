    def save_checkpoint(self, filepath, weights_only: bool = False):
        """Save model/training states as a checkpoint file through state-dump and file-write.

        Args:
            filepath: write-target file's path
            weights_only: saving model weights only
        """
        # dump states as a checkpoint dictionary object
        _checkpoint = self.lightning_module.trainer.checkpoint_connector.dump_checkpoint(weights_only)
        # Todo: TypeError: 'mappingproxy' object does not support item assignment
        self.save({k: v for k, v in _checkpoint.items() if k != "callbacks"}, filepath)