def my_app(cfg: Config) -> None:
    connection = instantiate(cfg.db)
    connection.connect()