    def execute(cls, app, sa_session, action, job, replacement_dict):
        # TODO Optimize this later.  Just making it work for now.
        # TODO Support purging as well as deletion if user_purge is enabled.
        # Dataset candidates for deletion must be
        # 1) Created by the workflow.
        # 2) Not have any job_to_input_dataset associations with states other
        # than OK or DELETED.  If a step errors, we don't want to delete/purge it
        # automatically.
        # 3) Not marked as a workflow output.
        # POTENTIAL ISSUES:  When many outputs are being finish()ed
        # concurrently, sometimes non-terminal steps won't be cleaned up
        # because of the lag in job state updates.
        sa_session.flush()
        if not job.workflow_invocation_step:
            log.debug("This job is not part of a workflow invocation, delete intermediates aborted.")
            return
        wfi = job.workflow_invocation_step.workflow_invocation
        sa_session.refresh(wfi)
        if wfi.active:
            log.debug("Workflow still scheduling so new jobs may appear, skipping deletion of intermediate files.")
            # Still evaluating workflow so we don't yet have all workflow invocation
            # steps to start looking at.
            return
        outputs_defined = wfi.workflow.has_outputs_defined()
        if outputs_defined:
            wfi_steps = [wfistep for wfistep in wfi.steps if not wfistep.workflow_step.workflow_outputs and wfistep.workflow_step.type == "tool"]
            jobs_to_check = []
            for wfi_step in wfi_steps:
                sa_session.refresh(wfi_step)
                wfi_step_job = wfi_step.job
                if wfi_step_job:
                    jobs_to_check.append(wfi_step_job)
                else:
                    log.debug("No job found yet for wfi_step %s, (step %s)" % (wfi_step, wfi_step.workflow_step))
            for j2c in jobs_to_check:
                creating_jobs = [(x, x.dataset.creating_job) for x in j2c.input_datasets if x.dataset.creating_job]
                for (x, creating_job) in creating_jobs:
                    sa_session.refresh(creating_job)
                    sa_session.refresh(x)
                for input_dataset in [x.dataset for (x, creating_job) in creating_jobs if creating_job.workflow_invocation_step and creating_job.workflow_invocation_step.workflow_invocation == wfi]:
                    safe_to_delete = True
                    for job_to_check in [d_j.job for d_j in input_dataset.dependent_jobs]:
                        if job_to_check != job and job_to_check.state not in [job.states.OK, job.states.DELETED]:
                            log.debug("Workflow Intermediates cleanup attempted, but non-terminal state '%s' detected for job %s" % (job_to_check.state, job_to_check.id))
                            safe_to_delete = False
                    if safe_to_delete:
                        # Support purging here too.
                        input_dataset.mark_deleted()
        else:
            # No workflow outputs defined, so we can't know what to delete.
            # We could make this work differently in the future
            pass