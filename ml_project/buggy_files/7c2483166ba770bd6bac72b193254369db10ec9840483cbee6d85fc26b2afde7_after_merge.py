  def create_graph(self, spec_roots):
    """Construct and return a BuildGraph given a set of input specs."""
    graph = self.legacy_graph_cls(self.scheduler, self.engine, self.symbol_table_cls)
    with self.scheduler.locked():
      for _ in graph.inject_specs_closure(spec_roots):  # Ensure the entire generator is unrolled.
        pass
    logger.debug('engine cache stats: %s', self.engine.cache_stats())
    logger.debug('build_graph is: %s', graph)
    return graph