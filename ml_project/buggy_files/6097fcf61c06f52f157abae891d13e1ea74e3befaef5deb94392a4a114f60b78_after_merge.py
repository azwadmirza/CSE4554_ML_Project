def experiment(_cfg: DictConfig) -> None:
    print(HydraConfig.get().job.name)