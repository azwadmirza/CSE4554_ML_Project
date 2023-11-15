    def to_internal_value(self, pk):
        try:
            pk = int(pk)
        except ValueError:
            self.fail('invalid')
        try:
            Credential.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(_('Credential {} does not exist').format(pk))
        return pk