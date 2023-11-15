def _format_job_instance(job):
    return {'Function': job['fun'],
            'Arguments': list(job.get('arg', [])),
            'Target': job['tgt'],
            'Target-type': job.get('tgt_type', []),
            'User': job.get('user', 'root')}