    def get_field_info(self, field):
        res = super(JobTypeMetadata, self).get_field_info(field)

        if field.field_name == 'job_type':
            res['choices'] = [
                choice for choice in res['choices']
                if choice[0] != 'scan'
            ]
        return res