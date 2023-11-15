    def can_compile(self, filename):
        suffix = filename.split('.')[-1]
        return suffix in ('vala', 'vapi')