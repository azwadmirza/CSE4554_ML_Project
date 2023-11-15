    def minimize(self, model, session=None, var_list=None, feed_dict=None,
                 maxiter=1000, initialize=True, anchor=True, **kwargs):
        """
        Minimizes objective function of the model.

        :param model: GPflow model with objective tensor.
        :param session: Session where optimization will be run.
        :param var_list: List of extra variables which should be trained during optimization.
        :param feed_dict: Feed dictionary of tensors passed to session run method.
        :param maxiter: Number of run interation.
        :param initialize: If `True` model parameters will be re-initialized even if they were
            initialized before for gotten session.
        :param anchor: If `True` trained variable values computed during optimization at
            particular session will be synchronized with internal parameter values.
        :param kwargs: This is a dictionary of extra parameters for session run method.
        """

        if model is None or not isinstance(model, Model):
            raise ValueError('Unknown type passed for optimization.')

        session = model.enquire_session(session)

        self._model = model
        objective = model.objective

        with session.graph.as_default():
            full_var_list = self._gen_var_list(model, var_list)

            # Create optimizer variables before initialization.
            self._minimize_operation = self.optimizer.minimize(
                objective, var_list=full_var_list, **kwargs)

            model.initialize(session=session, force=initialize)
            self._initialize_optimizer(session, full_var_list)

            feed_dict = self._gen_feed_dict(model, feed_dict)
            for _i in range(maxiter):
                session.run(self.minimize_operation, feed_dict=feed_dict)

        if anchor:
            model.anchor(session)