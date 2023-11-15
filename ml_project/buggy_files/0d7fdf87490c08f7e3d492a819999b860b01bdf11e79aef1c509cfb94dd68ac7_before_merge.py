def _format_job_instance(job):
    return {'Function': job['fun'],
            'Arguments': list(job['arg']),
            'Target': job['tgt'],
            'Target-type': job['tgt_type'],
            'User': job.get('user', 'root')}