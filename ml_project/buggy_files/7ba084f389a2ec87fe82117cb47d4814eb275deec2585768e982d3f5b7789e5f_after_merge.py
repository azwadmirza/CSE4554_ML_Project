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
                changed_by = force_text(user)
            except AttributeError:
                # AnonymousUser may not have USERNAME_FIELD
                changed_by = "anonymous"
            else:
                # limit changed_by and created_by to avoid problems with Custom User Model
                if len(changed_by) > constants.PAGE_USERNAME_MAX_LENGTH:
                    changed_by = u'{0}... (id={1})'.format(
                        changed_by[:constants.PAGE_USERNAME_MAX_LENGTH - 15],
                        user.pk,
                    )

            self.changed_by = changed_by

        else:
            self.changed_by = "script"
        if created:
            self.created_by = self.changed_by

        if commit:
            if not self.depth:
                if self.parent_id:
                    self.depth = self.parent.depth + 1
                    self.parent.add_child(instance=self)
                else:
                    self.add_root(instance=self)
                return  #add_root and add_child save as well
            super(Page, self).save(**kwargs)