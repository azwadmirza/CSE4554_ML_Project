    def match(self, cfn):
        """Check CloudFormation Resources"""

        matches = []

        for r_name, r_values in cfn.get_resources().items():
            update_policy = r_values.get('UpdatePolicy', {})
            resource_type = r_values.get('Type')
            if isinstance(update_policy, dict):
                for up_type, up_value in update_policy.items():
                    path = ['Resources', r_name, 'UpdatePolicy', up_type]
                    up_type_spec = self.valid_attributes.get('main').get(up_type)
                    if up_type_spec:
                        if resource_type not in up_type_spec.get('ResourceTypes'):
                            message = 'UpdatePolicy only supports this type for resources of type ({0})'
                            matches.append(
                                RuleMatch(path, message.format(', '.join(map(str, up_type_spec.get('ResourceTypes'))))))
                        if 'Type' in up_type_spec:
                            matches.extend(
                                self.check_attributes(
                                    up_value, up_type_spec.get('Type'), path[:]))

                        else:
                            matches.extend(
                                self.check_primitive_type(
                                    up_value, up_type_spec.get('PrimitiveType'),
                                    path[:],
                                    valid_values=up_type_spec.get('ValidValues', [])))
                    else:
                        message = 'UpdatePolicy doesn\'t support type {0}'
                        matches.append(
                            RuleMatch(path, message.format(up_type)))
            else:
                message = 'UpdatePolicy should be an object'
                matches.append(
                    RuleMatch(['Resources', r_name, 'UpdatePolicy'], message.format()))

        return matches