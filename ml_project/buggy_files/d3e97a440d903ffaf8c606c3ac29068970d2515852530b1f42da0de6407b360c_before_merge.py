    def validate(self, data):

        # Validate uniqueness of name and slug if a site has been assigned.
        if data.get('site', None):
            for field in ['name', 'slug']:
                validator = UniqueTogetherValidator(queryset=VLANGroup.objects.all(), fields=('site', field))
                validator.set_context(self)
                validator(data)

        # Enforce model validation
        super().validate(data)

        return data