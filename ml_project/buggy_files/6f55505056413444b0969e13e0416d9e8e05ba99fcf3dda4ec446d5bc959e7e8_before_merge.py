    def get_field_info(self, field):
        res = super(JobTypeMetadata, self).get_field_info(field)

        if field.field_name == 'job_type':
            index = 0
            for choice in res['choices']:
                if choice[0] == 'scan':
                    res['choices'].pop(index)
                    break
                index += 1
        return res