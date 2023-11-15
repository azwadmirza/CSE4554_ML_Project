    def get_vm(self):
        """
        Find unique virtual machine either by UUID, MoID or Name.
        Returns: virtual machine object if found, else None.

        """
        vm_obj = None
        user_desired_path = None
        use_instance_uuid = self.params.get('use_instance_uuid') or False
        if self.params['uuid'] and not use_instance_uuid:
            vm_obj = find_vm_by_id(self.content, vm_id=self.params['uuid'], vm_id_type="uuid")
        elif self.params['uuid'] and use_instance_uuid:
            vm_obj = find_vm_by_id(self.content,
                                   vm_id=self.params['uuid'],
                                   vm_id_type="instance_uuid")
        elif self.params['name']:
            objects = self.get_managed_objects_properties(vim_type=vim.VirtualMachine, properties=['name'])
            vms = []

            for temp_vm_object in objects:
                if len(temp_vm_object.propSet) != 1:
                    continue
                for temp_vm_object_property in temp_vm_object.propSet:
                    if temp_vm_object_property.val == self.params['name']:
                        vms.append(temp_vm_object.obj)
                        break

            # get_managed_objects_properties may return multiple virtual machine,
            # following code tries to find user desired one depending upon the folder specified.
            if len(vms) > 1:
                # We have found multiple virtual machines, decide depending upon folder value
                if self.params['folder'] is None:
                    self.module.fail_json(msg="Multiple virtual machines with same name [%s] found, "
                                              "Folder value is a required parameter to find uniqueness "
                                              "of the virtual machine" % self.params['name'],
                                          details="Please see documentation of the vmware_guest module "
                                                  "for folder parameter.")

                # Get folder path where virtual machine is located
                # User provided folder where user thinks virtual machine is present
                user_folder = self.params['folder']
                # User defined datacenter
                user_defined_dc = self.params['datacenter']
                # User defined datacenter's object
                datacenter_obj = find_datacenter_by_name(self.content, self.params['datacenter'])
                # Get Path for Datacenter
                dcpath = compile_folder_path_for_object(vobj=datacenter_obj)

                # Nested folder does not return trailing /
                if not dcpath.endswith('/'):
                    dcpath += '/'

                if user_folder in [None, '', '/']:
                    # User provided blank value or
                    # User provided only root value, we fail
                    self.module.fail_json(msg="vmware_guest found multiple virtual machines with same "
                                              "name [%s], please specify folder path other than blank "
                                              "or '/'" % self.params['name'])
                elif user_folder.startswith('/vm/'):
                    # User provided nested folder under VMware default vm folder i.e. folder = /vm/india/finance
                    user_desired_path = "%s%s%s" % (dcpath, user_defined_dc, user_folder)
                else:
                    # User defined datacenter is not nested i.e. dcpath = '/' , or
                    # User defined datacenter is nested i.e. dcpath = '/F0/DC0' or
                    # User provided folder starts with / and datacenter i.e. folder = /ha-datacenter/ or
                    # User defined folder starts with datacenter without '/' i.e.
                    # folder = DC0/vm/india/finance or
                    # folder = DC0/vm
                    user_desired_path = user_folder

                for vm in vms:
                    # Check if user has provided same path as virtual machine
                    actual_vm_folder_path = self.get_vm_path(content=self.content, vm_name=vm)
                    if not actual_vm_folder_path.startswith("%s%s" % (dcpath, user_defined_dc)):
                        continue
                    if user_desired_path in actual_vm_folder_path:
                        vm_obj = vm
                        break
            elif vms:
                # Unique virtual machine found.
                vm_obj = vms[0]
        elif self.params['moid']:
            vm_obj = VmomiSupport.templateOf('VirtualMachine')(self.params['moid'], self.si._stub)

        if vm_obj:
            self.current_vm_obj = vm_obj

        return vm_obj