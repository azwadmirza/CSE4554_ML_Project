    def _load_model_state(cls, checkpoint: Dict[str, Any], *cls_args, **cls_kwargs):
        cls_spec = inspect.getfullargspec(cls.__init__)
        cls_init_args_name = inspect.signature(cls).parameters.keys()
        # pass in the values we saved automatically
        if cls.CHECKPOINT_HYPER_PARAMS_KEY in checkpoint:
            model_args = {}

            # add some back compatibility, the actual one shall be last
            for hparam_key in CHECKPOINT_PAST_HPARAMS_KEYS + (cls.CHECKPOINT_HYPER_PARAMS_KEY,):
                if hparam_key in checkpoint:
                    model_args.update(checkpoint[hparam_key])

            model_args = _convert_loaded_hparams(model_args, checkpoint.get(cls.CHECKPOINT_HYPER_PARAMS_TYPE))

            args_name = checkpoint.get(cls.CHECKPOINT_HYPER_PARAMS_NAME)

            if args_name == 'kwargs':
                # in case the class cannot take any extra argument filter only the possible
                cls_kwargs.update(**model_args)
            elif args_name:
                if args_name in cls_init_args_name:
                    cls_kwargs.update({args_name: model_args})
            else:
                cls_args = (model_args,) + cls_args

        if not cls_spec.varkw:
            # filter kwargs according to class init unless it allows any argument via kwargs
            cls_kwargs = {k: v for k, v in cls_kwargs.items() if k in cls_init_args_name}

        # prevent passing positional arguments if class does not accept any
        if len(cls_spec.args) <= 1 and not cls_spec.kwonlyargs:
            cls_args, cls_kwargs = [], {}
        model = cls(*cls_args, **cls_kwargs)
        # load the state_dict on the model automatically
        model.load_state_dict(checkpoint['state_dict'])

        # give model a chance to load something
        model.on_load_checkpoint(checkpoint)

        return model