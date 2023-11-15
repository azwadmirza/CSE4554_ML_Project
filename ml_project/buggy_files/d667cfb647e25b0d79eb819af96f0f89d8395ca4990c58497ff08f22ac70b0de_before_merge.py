    def can_copy(self, obj):
        if self.save_messages:
            missing_ujt = []
            missing_credentials = []
            missing_inventories = []
            qs = obj.workflow_job_template_nodes
            qs = qs.prefetch_related('unified_job_template', 'inventory__use_role', 'credentials__use_role')
            for node in qs.all():
                node_errors = {}
                if node.inventory and self.user not in node.inventory.use_role:
                    missing_inventories.append(node.inventory.name)
                for cred in node.credentials.all():
                    if self.user not in cred.use_role:
                        missing_credentials.append(node.credential.name)
                ujt = node.unified_job_template
                if ujt and not self.user.can_access(UnifiedJobTemplate, 'start', ujt, validate_license=False):
                    missing_ujt.append(ujt.name)
                if node_errors:
                    wfjt_errors[node.id] = node_errors
            if missing_ujt:
                self.messages['templates_unable_to_copy'] = missing_ujt
            if missing_credentials:
                self.messages['credentials_unable_to_copy'] = missing_credentials
            if missing_inventories:
                self.messages['inventories_unable_to_copy'] = missing_inventories

        return self.check_related('organization', Organization, {'reference_obj': obj}, role_field='workflow_admin_role',
                                  mandatory=True)