def my_app(cfg: DictConfig) -> None:
    connection = instantiate(cfg.db)
    connection.connect()