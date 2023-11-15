    def iterate(dataset, batch_size, epochs):
      num_shards = len(shard_indices)
      if deterministic:
        shard_perm = np.arange(num_shards)

      # (ytz): Depending on the application, thread-based pools may be faster
      # than process based pools, since process based pools need to pickle/serialize
      # objects as an extra overhead. Also, as hideously as un-thread safe this looks,
      # we're actually protected by the GIL.
      pool = Pool(1)  # mp.dummy aliases ThreadPool to Pool

      if batch_size is None:
        num_global_batches = num_shards
      else:
        num_global_batches = math.ceil(dataset.get_shape()[0][0] / batch_size)

      for epoch in range(epochs):
        if not deterministic:
          shard_perm = np.random.permutation(num_shards)
        next_shard = pool.apply_async(dataset.get_shard,
                                      (shard_indices[shard_perm[0]],))
        cur_global_batch = 0
        cur_shard = 0
        carry = None

        while cur_global_batch < num_global_batches:

          X, y, w, ids = next_shard.get()
          if cur_shard < num_shards - 1:
            next_shard = pool.apply_async(
                dataset.get_shard, (shard_indices[shard_perm[cur_shard + 1]],))
          elif epoch == epochs - 1:
            pool.close()

          if carry is not None:
            X = np.concatenate([carry[0], X], axis=0)
            if y is not None:
              y = np.concatenate([carry[1], y], axis=0)
            if w is not None:
              w = np.concatenate([carry[2], w], axis=0)
            ids = np.concatenate([carry[3], ids], axis=0)
            carry = None

          n_shard_samples = X.shape[0]
          cur_local_batch = 0
          if batch_size is None:
            shard_batch_size = n_shard_samples
          else:
            shard_batch_size = batch_size

          if n_shard_samples == 0:
            cur_shard += 1
            if batch_size is None:
              cur_global_batch += 1
            continue

          num_local_batches = math.ceil(n_shard_samples / shard_batch_size)
          if not deterministic:
            sample_perm = np.random.permutation(n_shard_samples)
          else:
            sample_perm = np.arange(n_shard_samples)

          while cur_local_batch < num_local_batches:
            start = cur_local_batch * shard_batch_size
            end = min(n_shard_samples, (cur_local_batch + 1) * shard_batch_size)

            indices = range(start, end)
            perm_indices = sample_perm[indices]
            X_b = X[perm_indices]

            if y is not None:
              y_b = y[perm_indices]
            else:
              y_b = None

            if w is not None:
              w_b = w[perm_indices]
            else:
              w_b = None

            ids_b = ids[perm_indices]

            assert len(X_b) <= shard_batch_size
            if len(X_b) < shard_batch_size and cur_shard != num_shards - 1:
              assert carry is None
              carry = [X_b, y_b, w_b, ids_b]
            else:

              # (ytz): this skips everything except possibly the last shard
              if pad_batches:
                (X_b, y_b, w_b, ids_b) = pad_batch(shard_batch_size, X_b, y_b,
                                                   w_b, ids_b)

              yield X_b, y_b, w_b, ids_b
              cur_global_batch += 1
            cur_local_batch += 1
          cur_shard += 1