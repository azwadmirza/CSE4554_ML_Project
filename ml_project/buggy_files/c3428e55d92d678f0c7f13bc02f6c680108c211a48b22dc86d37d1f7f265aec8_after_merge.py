    def execute(self, image_obj, context):
        """
        Main entry point for the trigger execution. Will clear any previously saved exec state and call the evaluate() function.
        :param image_obj:
        :param context:
        :return:
        """
        self.reset()

        if self.gate_cls.__lifecycle_state__ != LifecycleStates.eol and self.__lifecycle_state__ != LifecycleStates.eol:
            if image_obj is None:
                raise TriggerEvaluationError(trigger=self, message='No image provided to evaluate against')
            try:
                self.evaluate(image_obj, context)
            except Exception as e:
                logger.exception('Error evaluating trigger. Aborting trigger execution')
                raise TriggerEvaluationError(trigger=self, message=str(e))

        return True