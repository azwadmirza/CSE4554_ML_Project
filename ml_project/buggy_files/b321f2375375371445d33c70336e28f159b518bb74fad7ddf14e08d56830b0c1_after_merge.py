    def __init__(self, weight_decay: Union[FloatTensorLike, Callable], **kwargs):
        """Extension class that adds weight decay to an optimizer.

        Args:
            weight_decay: A `Tensor`, a floating point value, or a schedule
                that is a `tf.keras.optimizers.schedules.LearningRateSchedule`
                to decay the variable by, in the update step.
            **kwargs: Optional list or tuple or set of `Variable` objects to
                decay.
        """
        wd = kwargs.pop("weight_decay", weight_decay)
        super().__init__(**kwargs)
        self._decay_var_list = None  # is set in minimize or apply_gradients
        self._set_hyper("weight_decay", wd)