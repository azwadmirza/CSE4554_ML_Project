    def get_lease(self):
        datastore, datacenter, resource_pool, network_mappings = self.get_objects()

        params = {
            'diskProvisioning': self.params['disk_provisioning'],
        }
        if self.params['name']:
            params['entityName'] = self.params['name']
        if network_mappings:
            params['networkMapping'] = network_mappings
        if self.params['deployment_option']:
            params['deploymentOption'] = self.params['deployment_option']
        if self.params['properties']:
            params['propertyMapping'] = []
            for key, value in self.params['properties'].items():
                property_mapping = vim.KeyValue()
                property_mapping.key = key
                property_mapping.value = str(value) if isinstance(value, bool) else value
                params['propertyMapping'].append(property_mapping)

        if self.params['folder']:
            folder = self.content.searchIndex.FindByInventoryPath(self.params['folder'])
            if not folder:
                self.module.fail_json(msg="Unable to find the specified folder %(folder)s" % self.params)
        else:
            folder = datacenter.vmFolder

        spec_params = vim.OvfManager.CreateImportSpecParams(**params)

        ovf_descriptor = self.get_ovf_descriptor()

        self.import_spec = self.content.ovfManager.CreateImportSpec(
            ovf_descriptor,
            resource_pool,
            datastore,
            spec_params
        )

        errors = [to_native(e.msg) for e in getattr(self.import_spec, 'error', [])]
        if self.params['fail_on_spec_warnings']:
            errors.extend(
                (to_native(w.msg) for w in getattr(self.import_spec, 'warning', []))
            )
        if errors:
            self.module.fail_json(
                msg='Failure validating OVF import spec: %s' % '. '.join(errors)
            )

        for warning in getattr(self.import_spec, 'warning', []):
            self.module.warn('Problem validating OVF import spec: %s' % to_native(warning.msg))

        if not self.params['allow_duplicates']:
            name = self.import_spec.importSpec.configSpec.name
            match = find_vm_by_name(self.content, name, folder=folder)
            if match:
                self.module.exit_json(instance=gather_vm_facts(self.content, match), changed=False)

        if self.module.check_mode:
            self.module.exit_json(changed=True, instance={'hw_name': name})

        try:
            self.lease = resource_pool.ImportVApp(
                self.import_spec.importSpec,
                folder
            )
        except vmodl.fault.SystemError as e:
            self.module.fail_json(
                msg='Failed to start import: %s' % to_native(e.msg)
            )

        while self.lease.state != vim.HttpNfcLease.State.ready:
            time.sleep(0.1)

        self.entity = self.lease.info.entity

        return self.lease, self.import_spec