    def barrier(self, name: Optional[str] = None) -> None:
        rendezvous(f"pl.Trainer.{name}")