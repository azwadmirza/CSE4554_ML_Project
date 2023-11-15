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
            if instance.nat_inside and instance.nat_inside.device is not None:
                initial['nat_site'] = instance.nat_inside.device.site
                initial['nat_rack'] = instance.nat_inside.device.rack
                initial['nat_device'] = instance.nat_inside.device
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