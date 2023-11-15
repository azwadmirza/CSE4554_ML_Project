def experiment(_cfg: DictConfig) -> None:
    hc = HydraConfig.instance()
    assert hc.hydra is not None
    print(hc.hydra.job.name)