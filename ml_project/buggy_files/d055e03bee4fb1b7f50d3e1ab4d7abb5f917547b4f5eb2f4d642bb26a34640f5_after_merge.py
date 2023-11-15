    def _get_metric_interpolated_filepath_name(
        self,
        ckpt_name_metrics: Dict[str, Any],
        epoch: int,
        step: int,
        trainer,
        del_filepath: Optional[str] = None,
    ) -> str:
        filepath = self.format_checkpoint_name(epoch, step, ckpt_name_metrics)

        version_cnt = 0
        while self.file_exists(filepath, trainer) and filepath != del_filepath:
            filepath = self.format_checkpoint_name(epoch, step, ckpt_name_metrics, ver=version_cnt)
            version_cnt += 1

        return filepath