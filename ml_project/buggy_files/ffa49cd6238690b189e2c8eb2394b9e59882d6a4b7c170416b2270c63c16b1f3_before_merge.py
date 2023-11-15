    def create_slcwa_instances(self) -> Instances:
        """Create sLCWA instances for this factory's triples."""
        return SLCWAInstances(mapped_triples=self.mapped_triples)