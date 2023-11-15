    def return_user_exc(self, builder, exc, exc_args=None, loc=None,
                        func_name=None):
        try_info = getattr(builder, '_in_try_block', False)
        self.set_static_user_exc(builder, exc, exc_args=exc_args,
                                   loc=loc, func_name=func_name)
        trystatus = self.check_try_status(builder)
        if try_info:
            # This is a hack for old-style impl.
            # We will branch directly to the exception handler.
            builder.branch(try_info['target'])
        else:
            # Return from the current function
            self._return_errcode_raw(builder, RETCODE_USEREXC)