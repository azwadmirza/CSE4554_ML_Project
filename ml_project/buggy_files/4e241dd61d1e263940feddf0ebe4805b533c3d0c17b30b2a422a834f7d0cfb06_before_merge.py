def run_task_manager():
    if migration_in_progress_check_or_relase():
        logger.debug("Not running task manager because migration is in progress.")
        return
    logger.debug("Running Tower task manager.")
    TaskManager().schedule()