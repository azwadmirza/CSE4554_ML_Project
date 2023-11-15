def worker_task(ps, batch_size=50):
    # Download MNIST.
    mnist = input_data.read_data_sets("MNIST_data", one_hot=True)

    # Initialize the model.
    net = model.SimpleCNN()
    keys = net.get_weights()[0]

    while True:
        # Get the current weights from the parameter server.
        weights = ray.get(ps.pull.remote(keys))
        net.set_weights(keys, weights)

        # Compute an update and push it to the parameter server.
        xs, ys = mnist.train.next_batch(batch_size)
        gradients = net.compute_update(xs, ys)
        ps.push.remote(keys, gradients)