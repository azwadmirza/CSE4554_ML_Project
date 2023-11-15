    def clean_repo_link(self):
        """Validate repository link."""
        try:
            repo = Component.objects.get_linked(self.repo)
            if repo is not None and repo.is_repo_link:
                raise ValidationError(
                    {
                        "repo": _(
                            "Invalid link to a Weblate project, "
                            "cannot link to linked repository!"
                        )
                    }
                )
            if repo.pk == self.pk:
                raise ValidationError(
                    {
                        "repo": _(
                            "Invalid link to a Weblate project, "
                            "cannot link it to itself!"
                        )
                    }
                )
        except (Component.DoesNotExist, ValueError):
            raise ValidationError(
                {
                    "repo": _(
                        "Invalid link to a Weblate project, "
                        "use weblate://project/component."
                    )
                }
            )
        for setting in ("push", "branch", "git_export"):
            # The git_export might be missing in case of form validation
            if getattr(self, setting, None):
                raise ValidationError(
                    {setting: _("Option is not available for linked repositories.")}
                )
        self.linked_component = Component.objects.get_linked(self.repo)