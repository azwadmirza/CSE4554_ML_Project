    def clean(self):

        if self.address:

            # /0 masks are not acceptable
            if self.address.prefixlen == 0:
                raise ValidationError({
                    'address': "Cannot create IP address with /0 mask."
                })

            # Enforce unique IP space (if applicable)
            if self.role not in IPADDRESS_ROLES_NONUNIQUE and ((
                self.vrf is None and settings.ENFORCE_GLOBAL_UNIQUE
            ) or (
                self.vrf and self.vrf.enforce_unique
            )):
                duplicate_ips = self.get_duplicates()
                if duplicate_ips:
                    raise ValidationError({
                        'address': "Duplicate IP address found in {}: {}".format(
                            "VRF {}".format(self.vrf) if self.vrf else "global table",
                            duplicate_ips.first(),
                        )
                    })

        # Check for primary IP assignment that doesn't match the assigned device/VM
        if self.pk and type(self.assigned_object) is Interface:
            device = Device.objects.filter(Q(primary_ip4=self) | Q(primary_ip6=self)).first()
            if device:
                if self.assigned_object is None:
                    raise ValidationError({
                        'interface': f"IP address is primary for device {device} but not assigned to an interface"
                    })
                elif self.assigned_object.device != device:
                    raise ValidationError({
                        'interface': f"IP address is primary for device {device} but assigned to "
                                     f"{self.assigned_object.device} ({self.assigned_object})"
                    })
        elif self.pk and type(self.assigned_object) is VMInterface:
            vm = VirtualMachine.objects.filter(Q(primary_ip4=self) | Q(primary_ip6=self)).first()
            if vm:
                if self.assigned_object is None:
                    raise ValidationError({
                        'vminterface': f"IP address is primary for virtual machine {vm} but not assigned to an "
                                       f"interface"
                    })
                elif self.interface.virtual_machine != vm:
                    raise ValidationError({
                        'vminterface': f"IP address is primary for virtual machine {vm} but assigned to "
                                       f"{self.assigned_object.virtual_machine} ({self.assigned_object})"
                    })