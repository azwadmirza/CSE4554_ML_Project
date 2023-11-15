    def __str__(self):
        try:
            device = self.device
        except Device.DoesNotExist:
            device = None
        if self.role and device and self.name:
            return '{} for {} ({})'.format(self.role, self.device, self.name)
        # Return role and device if no name is set
        if self.role and device:
            return '{} for {}'.format(self.role, self.device)
        return 'Secret'