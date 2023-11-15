    def barrier(self, name: Optional[str] = None) -> None:
        if torch_distrib.is_initialized():
            rendezvous(f"pl.Trainer.{name}")