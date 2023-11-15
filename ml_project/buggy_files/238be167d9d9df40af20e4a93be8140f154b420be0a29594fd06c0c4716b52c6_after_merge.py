    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()
        if instance:
            if type(instance.assigned_object) is Interface:
                initial['device'] = instance.assigned_object.device
                initial['interface'] = instance.assigned_object
            elif type(instance.assigned_object) is VMInterface:
                initial['virtual_machine'] = instance.assigned_object.virtual_machine
                initial['vminterface'] = instance.assigned_object
            if instance.nat_inside:
                nat_inside_parent = instance.nat_inside.assigned_object
                if type(nat_inside_parent) is Interface:
                    initial['nat_site'] = nat_inside_parent.device.site.pk
                    initial['nat_rack'] = nat_inside_parent.device.rack.pk
                    initial['nat_device'] = nat_inside_parent.device.pk
                elif type(nat_inside_parent) is VMInterface:
                    initial['nat_cluster'] = nat_inside_parent.virtual_machine.cluster.pk
                    initial['nat_virtual_machine'] = nat_inside_parent.virtual_machine.pk
        kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

        self.fields['vrf'].empty_label = 'Global'

        # Initialize primary_for_parent if IP address is already assigned
        if self.instance.pk and self.instance.assigned_object:
            parent = self.instance.assigned_object.parent
            if (
                self.instance.address.version == 4 and parent.primary_ip4_id == self.instance.pk or
                self.instance.address.version == 6 and parent.primary_ip6_id == self.instance.pk
            ):
                self.initial['primary_for_parent'] = True