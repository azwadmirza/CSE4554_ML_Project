    def _get_best_study_config(self):
        metadata = {
            'best_trial_number': self.study.best_trial.number,
            'best_trial_evaluation': self.study.best_value,
        }

        pipeline_config = dict()
        for k, v in self.study.user_attrs.items():
            if k.startswith('pykeen_'):
                metadata[k[len('pykeen_'):]] = v
            elif k in {'metric'}:
                continue
            else:
                pipeline_config[k] = v

        for field in dataclasses.fields(self.objective):
            field_value = getattr(self.objective, field.name)
            if not field_value:
                continue
            if field.name.endswith('_kwargs'):
                logger.debug(f'saving pre-specified field in pipeline config: {field.name}={field_value}')
                pipeline_config[field.name] = field_value
            elif field.name in {'training', 'testing', 'validation'}:
                pipeline_config[field.name] = field_value if isinstance(field_value, str) else USER_DEFINED_CODE

        for k, v in self.study.best_params.items():
            sk, ssk = k.split('.')
            sk = f'{sk}_kwargs'
            if sk not in pipeline_config:
                pipeline_config[sk] = {}
            logger.debug(f'saving optimized field in pipeline config: {sk}.{ssk}={v}')
            pipeline_config[sk][ssk] = v

        for k in ('stopper', 'stopper_kwargs'):
            if k in pipeline_config:
                v = pipeline_config.pop(k)
                metadata[f'_{k}_removed_comment'] = f'{k} config removed after HPO: {v}'

        stopped_epoch = self.study.best_trial.user_attrs.get(STOPPED_EPOCH_KEY)
        if stopped_epoch is not None:
            old_num_epochs = pipeline_config['training_kwargs']['num_epochs']
            metadata['_stopper_comment'] = (
                f'While the original config had {old_num_epochs},'
                f' early stopping will now switch it to {int(stopped_epoch)}'
            )
            pipeline_config['training_kwargs']['num_epochs'] = int(stopped_epoch)
        return dict(metadata=metadata, pipeline=pipeline_config)