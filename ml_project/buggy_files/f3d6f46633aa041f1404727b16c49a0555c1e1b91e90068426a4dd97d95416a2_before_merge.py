    def return_exception(self, exc_class, exc_args=None, loc=None):
        self.call_conv.return_user_exc(self.builder, exc_class, exc_args,
                                       loc=loc,
                                       func_name=self.func_ir.func_id.func_name)