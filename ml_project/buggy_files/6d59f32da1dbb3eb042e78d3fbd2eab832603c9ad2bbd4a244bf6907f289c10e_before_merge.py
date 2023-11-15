    def __init__(
        self,
        representation_tree,
        dtype,
        device,
        matrix_shape,
        batch_shape=torch.Size(),
        inv_quad=False,
        logdet=False,
        preconditioner=None,
        logdet_correction=None,
        probe_vectors=None,
        probe_vector_norms=None,
    ):
        if not (inv_quad or logdet):
            raise RuntimeError("Either inv_quad or logdet must be true (or both)")

        self.representation_tree = representation_tree
        self.dtype = dtype
        self.device = device
        self.matrix_shape = matrix_shape
        self.batch_shape = batch_shape
        self.inv_quad = inv_quad
        self.logdet = logdet
        self.preconditioner = preconditioner
        self.logdet_correction = logdet_correction

        if (probe_vectors is None or probe_vector_norms is None) and logdet:
            num_random_probes = settings.num_trace_samples.value()
            probe_vectors = torch.empty(matrix_shape[-1], num_random_probes, dtype=dtype, device=device)
            probe_vectors.bernoulli_().mul_(2).add_(-1)
            probe_vector_norms = torch.norm(probe_vectors, 2, dim=-2, keepdim=True)
            if batch_shape is not None:
                probe_vectors = probe_vectors.expand(*batch_shape, matrix_shape[-1], num_random_probes)
                probe_vector_norms = probe_vector_norms.expand(*batch_shape, 1, num_random_probes)
            probe_vectors = probe_vectors.div(probe_vector_norms)

        self.probe_vectors = probe_vectors
        self.probe_vector_norms = probe_vector_norms