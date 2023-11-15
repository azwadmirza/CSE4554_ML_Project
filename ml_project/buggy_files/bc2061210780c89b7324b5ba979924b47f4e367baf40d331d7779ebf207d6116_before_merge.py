    def to_internal_value(self, pk):
        try:
            Credential.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(_('Credential {} does not exist').format(pk))
        return pk