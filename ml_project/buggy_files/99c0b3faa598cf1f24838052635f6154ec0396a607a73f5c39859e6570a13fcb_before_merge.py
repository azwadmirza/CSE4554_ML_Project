    def _load_model_state(cls, checkpoint: Dict[str, Any], *cls_args, **cls_kwargs):
        # pass in the values we saved automatically
        if cls.CHECKPOINT_HYPER_PARAMS_KEY in checkpoint:
            model_args = {}

            # add some back compatibility, the actual one shall be last
            for hparam_key in CHECKPOINT_PAST_HPARAMS_KEYS + (cls.CHECKPOINT_HYPER_PARAMS_KEY,):
                if hparam_key in checkpoint:
                    model_args.update(checkpoint[hparam_key])

            if cls.CHECKPOINT_HYPER_PARAMS_TYPE in checkpoint:
                model_args = checkpoint[cls.CHECKPOINT_HYPER_PARAMS_TYPE](model_args)

            args_name = checkpoint.get(cls.CHECKPOINT_HYPER_PARAMS_NAME)
            cls_spec = inspect.getfullargspec(cls.__init__)
            kwargs_identifier = cls_spec.varkw
            cls_init_args_name = inspect.signature(cls).parameters.keys()

            if args_name == 'kwargs':
                # in case the class cannot take any extra argument filter only the possible
                if not kwargs_identifier:
                    model_args = {k: v for k, v in model_args.items() if k in cls_init_args_name}
                cls_kwargs.update(**model_args)
            elif args_name:
                if args_name in cls_init_args_name:
                    cls_kwargs.update({args_name: model_args})
            else:
                cls_args = (model_args,) + cls_args

        # load the state_dict on the model automatically
        model = cls(*cls_args, **cls_kwargs)
        model.load_state_dict(checkpoint['state_dict'])

        # give model a chance to load something
        model.on_load_checkpoint(checkpoint)

        return model