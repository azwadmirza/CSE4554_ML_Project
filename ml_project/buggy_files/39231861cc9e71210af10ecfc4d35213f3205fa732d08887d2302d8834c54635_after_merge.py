    def get_user_capabilities(self, obj, method_list=[], parent_obj=None, capabilities_cache={}):
        if obj is None:
            return {}
        user_capabilities = {}

        # Custom ordering to loop through methods so we can reuse earlier calcs
        for display_method in ['edit', 'delete', 'start', 'schedule', 'copy', 'adhoc', 'unattach']:
            if display_method not in method_list:
                continue

            if not settings.MANAGE_ORGANIZATION_AUTH and isinstance(obj, (Team, User)):
                user_capabilities[display_method] = self.user.is_superuser
                continue

            # Actions not possible for reason unrelated to RBAC
            # Cannot copy with validation errors, or update a manual group/project
            if 'write' not in getattr(self.user, 'oauth_scopes', ['write']):
                user_capabilities[display_method] = False  # Read tokens cannot take any actions
                continue
            elif display_method in ['copy', 'start', 'schedule'] and isinstance(obj, JobTemplate):
                if obj.validation_errors:
                    user_capabilities[display_method] = False
                    continue
            elif display_method == 'copy' and isinstance(obj, WorkflowJobTemplate) and obj.organization_id is None:
                user_capabilities[display_method] = self.user.is_superuser
                continue
            elif display_method == 'copy' and isinstance(obj, Project) and obj.scm_type == '':
                # Cannot copy manual project without errors
                user_capabilities[display_method] = False
                continue
            elif display_method in ['start', 'schedule'] and isinstance(obj, (Project)):
                if obj.scm_type == '':
                    user_capabilities[display_method] = False
                    continue

            # Grab the answer from the cache, if available
            if display_method in capabilities_cache:
                user_capabilities[display_method] = capabilities_cache[display_method]
                if self.user.is_superuser and not user_capabilities[display_method]:
                    # Cache override for models with bad orphaned state
                    user_capabilities[display_method] = True
                continue

            # Aliases for going form UI language to API language
            if display_method == 'edit':
                method = 'change'
            elif display_method == 'adhoc':
                method = 'run_ad_hoc_commands'
            else:
                method = display_method

            # Shortcuts in certain cases by deferring to earlier property
            if display_method == 'schedule':
                user_capabilities['schedule'] = user_capabilities['start']
                continue
            elif display_method == 'delete' and not isinstance(obj, (User, UnifiedJob, CustomInventoryScript, CredentialInputSource)):
                user_capabilities['delete'] = user_capabilities['edit']
                continue
            elif display_method == 'copy' and isinstance(obj, (Group, Host)):
                user_capabilities['copy'] = user_capabilities['edit']
                continue

            # Compute permission
            user_capabilities[display_method] = self.get_method_capability(method, obj, parent_obj)

        return user_capabilities