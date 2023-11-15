    def __determine_job_destination(self, params, raw_job_destination=None):
        if self.job_wrapper.tool is None:
            raise JobMappingException(
                "Can't map job to destination, tool '%s' is unavailable" % self.job_wrapper.get_job().tool_id
            )
        if raw_job_destination is None:
            raw_job_destination = self.job_wrapper.tool.get_job_destination(params)
        if raw_job_destination.runner == DYNAMIC_RUNNER_NAME:
            job_destination = self.__handle_dynamic_job_destination(raw_job_destination)
            log.debug("(%s) Mapped job to destination id: %s", self.job_wrapper.job_id, job_destination.id)
            # Recursively handle chained dynamic destinations
            if job_destination.runner == DYNAMIC_RUNNER_NAME:
                return self.__determine_job_destination(params, raw_job_destination=job_destination)
        else:
            job_destination = raw_job_destination
            log.debug("(%s) Mapped job to destination id: %s", self.job_wrapper.job_id, job_destination.id)
        return job_destination