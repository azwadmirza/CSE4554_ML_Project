    def execute(self, context):
        emr_hook = EmrHook(aws_conn_id=self.aws_conn_id)

        emr = emr_hook.get_conn()

        job_flow_id = self.job_flow_id or emr_hook.get_cluster_id_by_name(self.job_flow_name,
                                                                          self.cluster_states)
        if not job_flow_id:
            raise AirflowException('No cluster found for name: ' + self.job_flow_name)

        if self.do_xcom_push:
            context['ti'].xcom_push(key='job_flow_id', value=job_flow_id)

        self.log.info('Adding steps to %s', job_flow_id)
        response = emr.add_job_flow_steps(JobFlowId=job_flow_id, Steps=self.steps)

        if not response['ResponseMetadata']['HTTPStatusCode'] == 200:
            raise AirflowException('Adding steps failed: %s' % response)
        else:
            self.log.info('Steps %s added to JobFlow', response['StepIds'])
            return response['StepIds']