    def save(self, no_signals=False, commit=True, **kwargs):
        """
        Args:
            commit: True if model should be really saved
        """
        # delete template cache
        if hasattr(self, '_template_cache'):
            delattr(self, '_template_cache')

        created = not bool(self.pk)
        if self.reverse_id == "":
            self.reverse_id = None
        if self.application_namespace == "":
            self.application_namespace = None
        from cms.utils.permissions import _thread_locals

        user = getattr(_thread_locals, "user", None)
        if user:
            try:
                self.changed_by = str(user)
            except AttributeError:
                # AnonymousUser may not have USERNAME_FIELD
                self.changed_by = "anonymous"
        else:
            self.changed_by = "script"
        if created:
            self.created_by = self.changed_by
        if commit:
            if not self.depth:
                if self.parent_id:
                    self.parent.add_child(instance=self)
                else:
                    self.add_root(instance=self)
                return  #add_root and add_child save as well
            super(Page, self).save(**kwargs)