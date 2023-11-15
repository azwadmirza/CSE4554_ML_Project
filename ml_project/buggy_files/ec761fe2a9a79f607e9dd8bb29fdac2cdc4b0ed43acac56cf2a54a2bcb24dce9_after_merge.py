    def _save_tree(self):
        """recursively traverse back up the tree, save when we reach the root"""
        if self._parent:
            self._parent._save_tree()
        elif self._db_obj:
            if not self._db_obj.pk:
                cls_name = self.__class__.__name__
                non_saver_name = cls_name.lstrip("_Saver")
                err_msg = "%s %s has had its root Attribute deleted." % (cls_name, self)
                err_msg += " It must be cast to a %s before it can be modified further." % non_saver_name
                raise ValueError(err_msg)
            self._db_obj.value = self
        else:
            logger.log_err("_SaverMutable %s has no root Attribute to save to." % self)