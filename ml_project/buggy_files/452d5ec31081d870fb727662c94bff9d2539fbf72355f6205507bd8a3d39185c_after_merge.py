def my_app(cfg: DictConfig):
    env = submitit.JobEnvironment()
    log.info(f"Process ID {os.getpid()} executing task {cfg.task}, with {env}")
    time.sleep(1)