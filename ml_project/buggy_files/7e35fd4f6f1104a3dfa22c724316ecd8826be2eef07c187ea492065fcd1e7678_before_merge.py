    def save(self, *args, **kwargs):
        """
        Central database save operation.

        Notes:
            Arguments as per Django documentation.
            Calls `self.at_<fieldname>_postsave(new)`
            (this is a wrapper set by oobhandler:
            self._oob_at_<fieldname>_postsave())

        """
        global _MONITOR_HANDLER
        if not _MONITOR_HANDLER:
            from evennia.scripts.monitorhandler import MONITOR_HANDLER as _MONITOR_HANDLER

        if _IS_SUBPROCESS:
            # we keep a store of objects modified in subprocesses so
            # we know to update their caches in the central process
            global PROC_MODIFIED_COUNT, PROC_MODIFIED_OBJS
            PROC_MODIFIED_COUNT += 1
            PROC_MODIFIED_OBJS[PROC_MODIFIED_COUNT] = self

        if _IS_MAIN_THREAD:
            # in main thread - normal operation
            super(SharedMemoryModel, self).save(*args, **kwargs)
        else:
            # in another thread; make sure to save in reactor thread
            def _save_callback(cls, *args, **kwargs):
                super(SharedMemoryModel, cls).save(*args, **kwargs)
            callFromThread(_save_callback, self, *args, **kwargs)

        # update field-update hooks and eventual OOB watchers
        new = False
        if "update_fields" in kwargs and kwargs["update_fields"]:
            # get field objects from their names
            update_fields = (self._meta.get_field(fieldname)
                             for fieldname in kwargs.get("update_fields"))
        else:
            # meta.fields are already field objects; get them all
            new = True
            update_fields = self._meta.fields
        for field in update_fields:
            fieldname = field.name
            # trigger eventual monitors
            _MONITOR_HANDLER.at_update(self, fieldname)
            # if a hook is defined it must be named exactly on this form
            hookname = "at_%s_postsave" % fieldname
            if hasattr(self, hookname) and callable(_GA(self, hookname)):
                _GA(self, hookname)(new)