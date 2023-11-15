def reap(instance=None, status='failed', excluded_uuids=[]):
    '''
    Reap all jobs in waiting|running for this instance.
    '''
    me = instance
    if me is None:
        (changed, me) = Instance.objects.get_or_register()
        if changed:
            logger.info("Registered tower node '{}'".format(me.hostname))
    now = tz_now()
    workflow_ctype_id = ContentType.objects.get_for_model(WorkflowJob).id
    jobs = UnifiedJob.objects.filter(
        (
            Q(status='running') |
            Q(status='waiting', modified__lte=now - timedelta(seconds=60))
        ) & (
            Q(execution_node=me.hostname) |
            Q(controller_node=me.hostname)
        ) & ~Q(polymorphic_ctype_id=workflow_ctype_id)
    ).exclude(celery_task_id__in=excluded_uuids)
    for j in jobs:
        reap_job(j, status)