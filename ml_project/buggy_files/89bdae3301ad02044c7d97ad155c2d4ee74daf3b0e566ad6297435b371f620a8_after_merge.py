    def process(self, message):
        handler_function = self.message_types.get(type(message), None)

        if not handler_function:
            msg = 'Handler function for message type "%s" is not defined.' % type(message)
            raise ValueError(msg)

        try:
            handler_function(message)
        except Exception as e:
            # If the exception is caused by DB connection error, then the following
            # error handling routine will fail as well because it will try to update
            # the database and fail the workflow execution gracefully. In this case,
            # the garbage collector will find and cancel these workflow executions.
            self.fail_workflow_execution(message, e)