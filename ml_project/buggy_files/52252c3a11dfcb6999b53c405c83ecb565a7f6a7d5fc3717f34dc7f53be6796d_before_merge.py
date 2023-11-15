    def __str__(self):
        if self.role and self.device and self.name:
            return '{} for {} ({})'.format(self.role, self.device, self.name)
        # Return role and device if no name is set
        if self.role and self.device:
            return '{} for {}'.format(self.role, self.device)
        return 'Secret'