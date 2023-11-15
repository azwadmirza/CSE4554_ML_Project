def my_app(cfg: DictConfig):
    log.info(f"Process ID {os.getpid()} executing task {cfg.task} ...")

    time.sleep(1)