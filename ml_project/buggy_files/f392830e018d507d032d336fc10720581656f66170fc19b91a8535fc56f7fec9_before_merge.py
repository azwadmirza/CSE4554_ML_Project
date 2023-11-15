    def create_config_from_prompts(self, kwargs):
        '''
        Create a launch configuration entry for this job, given prompts
        returns None if it can not be created
        '''
        if self.unified_job_template is None:
            return None
        JobLaunchConfig = self._meta.get_field('launch_config').related_model
        config = JobLaunchConfig(job=self)
        valid_fields = self.unified_job_template.get_ask_mapping().keys()
        if hasattr(self, 'extra_vars'):
            valid_fields.extend(['survey_passwords', 'extra_vars'])
        for field_name, value in kwargs.items():
            if field_name not in valid_fields:
                raise Exception('Unrecognized launch config field {}.'.format(field_name))
            if field_name == 'credentials':
                continue
            key = field_name
            if key == 'extra_vars':
                key = 'extra_data'
            setattr(config, key, value)
        config.save()

        job_creds = (set(kwargs.get('credentials', [])) -
                     set(self.unified_job_template.credentials.all()))
        if job_creds:
            config.credentials.add(*job_creds)
        return config