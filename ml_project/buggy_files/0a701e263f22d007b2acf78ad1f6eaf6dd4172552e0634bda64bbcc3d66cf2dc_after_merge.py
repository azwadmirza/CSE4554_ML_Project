    def random(self, point=None, size=None):
        # Convert size to tuple
        size = to_tuple(size)
        # Draw mixture weights and a sample from each mixture to infer shape
        with _DrawValuesContext() as draw_context:
            # We first need to check w and comp_tmp shapes and re compute size
            w = draw_values([self.w], point=point, size=size)[0]
        with _DrawValuesContextBlocker():
            # We don't want to store the values drawn here in the context
            # because they wont have the correct size
            comp_tmp = self._comp_samples(point=point, size=None)

        # When size is not None, it's hard to tell the w parameter shape
        if size is not None and w.shape[:len(size)] == size:
            w_shape = w.shape[len(size):]
        else:
            w_shape = w.shape

        # Try to determine parameter shape and dist_shape
        param_shape = np.broadcast(np.empty(w_shape),
                                   comp_tmp).shape
        if np.asarray(self.shape).size != 0:
            dist_shape = np.broadcast(np.empty(self.shape),
                                      np.empty(param_shape[:-1])).shape
        else:
            dist_shape = param_shape[:-1]

        # When size is not None, maybe dist_shape partially overlaps with size
        if size is not None:
            if size == dist_shape:
                size = None
            elif size[-len(dist_shape):] == dist_shape:
                size = size[:len(size) - len(dist_shape)]

        # We get an integer _size instead of a tuple size for drawing the
        # mixture, then we just reshape the output
        if size is None:
            _size = None
        else:
            _size = int(np.prod(size))

        # Now we must broadcast w to the shape that considers size, dist_shape
        # and param_shape. However, we must take care with the cases in which
        # dist_shape and param_shape overlap
        if size is not None and w.shape[:len(size)] == size:
            if w.shape[:len(size + dist_shape)] != (size + dist_shape):
                # To allow w to broadcast, we insert new axis in between the
                # "size" axis and the "mixture" axis
                _w = w[(slice(None),) * len(size) +  # Index the size axis
                       (np.newaxis,) * len(dist_shape) +  # Add new axis for the dist_shape
                       (slice(None),)]  # Close with the slice of mixture components
                w = np.broadcast_to(_w, size + dist_shape + (param_shape[-1],))
        elif size is not None:
            w = np.broadcast_to(w, size + dist_shape + (param_shape[-1],))
        else:
            w = np.broadcast_to(w, dist_shape + (param_shape[-1],))

        # Compute the total size of the mixture's random call with size
        if _size is not None:
            output_size = int(_size * np.prod(dist_shape) * param_shape[-1])
        else:
            output_size = int(np.prod(dist_shape) * param_shape[-1])
        # Get the size we need for the mixture's random call
        mixture_size = int(output_size // np.prod(comp_tmp.shape))
        if mixture_size == 1 and _size is None:
            mixture_size = None

        # Semiflatten the mixture weights. The last axis is the number of
        # mixture mixture components, and the rest is all about size,
        # dist_shape and broadcasting
        w = np.reshape(w, (-1, w.shape[-1]))
        # Normalize mixture weights
        w = w / w.sum(axis=-1, keepdims=True)

        w_samples = generate_samples(random_choice,
                                     p=w,
                                     broadcast_shape=w.shape[:-1] or (1,),
                                     dist_shape=w.shape[:-1] or (1,),
                                     size=size)
        # Sample from the mixture
        with draw_context:
            mixed_samples = self._comp_samples(point=point,
                                               size=mixture_size)
        w_samples = w_samples.flatten()
        # Semiflatten the mixture to be able to zip it with w_samples
        mixed_samples = np.reshape(mixed_samples, (-1, comp_tmp.shape[-1]))
        # Select the samples from the mixture
        samples = np.array([mixed[choice] for choice, mixed in
                            zip(w_samples, mixed_samples)])
        # Reshape the samples to the correct output shape
        if size is None:
            samples = np.reshape(samples, dist_shape)
        else:
            samples = np.reshape(samples, size + dist_shape)
        return samples