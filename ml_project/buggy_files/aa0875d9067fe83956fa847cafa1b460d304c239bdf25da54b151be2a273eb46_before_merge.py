    def to_internal_value(self, data):
        # TODO: remove when API v1 is removed
        if 'credential_type' not in data and self.version == 1:
            # If `credential_type` is not provided, assume the payload is a
            # v1 credential payload that specifies a `kind` and a flat list
            # of field values
            #
            # In this scenario, we should automatically detect the proper
            # CredentialType based on the provided values
            kind = data.get('kind', 'ssh')
            credential_type = CredentialType.from_v1_kind(kind, data)
            if credential_type is None:
                raise serializers.ValidationError({"kind": _('"%s" is not a valid choice' % kind)})
            data['credential_type'] = credential_type.pk
            value = OrderedDict(
                {'credential_type': credential_type}.items() +
                super(CredentialSerializer, self).to_internal_value(data).items()
            )

            # Make a set of the keys in the POST/PUT payload
            # - Subtract real fields (name, organization, inputs)
            # - Subtract virtual v1 fields defined on the determined credential
            #   type (username, password, etc...)
            # - Any leftovers are invalid for the determined credential type
            valid_fields = set(super(CredentialSerializer, self).get_fields().keys())
            valid_fields.update(V2CredentialFields().get_fields().keys())
            valid_fields.update(['kind', 'cloud'])

            for field in set(data.keys()) - valid_fields - set(credential_type.defined_fields):
                if data.get(field):
                    raise serializers.ValidationError(
                        {"detail": _("'%s' is not a valid field for %s") % (field, credential_type.name)}
                    )
            value.pop('kind', None)
            return value
        return super(CredentialSerializer, self).to_internal_value(data)