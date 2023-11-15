    def _save_tree(self):
        """recursively traverse back up the tree, save when we reach the root"""
        if self._parent:
            self._parent._save_tree()
        elif self._db_obj:
            self._db_obj.value = self
        else:
            logger.log_err("_SaverMutable %s has no root Attribute to save to." % self)