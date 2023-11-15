def main(args):
    encoder_init, encode = encoder(args.hidden_dim, args.z_dim)
    decoder_init, decode = decoder(args.hidden_dim, 28 * 28)
    opt_init, opt_update, get_params = optimizers.adam(args.learning_rate)
    svi_init, svi_update, svi_eval = svi(model, guide, elbo, opt_init, opt_update, get_params,
                                         encode=encode, decode=decode, z_dim=args.z_dim)
    rng = PRNGKey(0)
    train_init, train_fetch = load_dataset(MNIST, batch_size=args.batch_size, split='train')
    test_init, test_fetch = load_dataset(MNIST, batch_size=args.batch_size, split='test')
    num_train, train_idx = train_init()
    rng, rng_enc, rng_dec, rng_binarize, rng_init = random.split(rng, 5)
    _, encoder_params = encoder_init(rng_enc, (args.batch_size, 28 * 28))
    _, decoder_params = decoder_init(rng_dec, (args.batch_size, args.z_dim))
    params = {'encoder': encoder_params, 'decoder': decoder_params}
    sample_batch = binarize(rng_binarize, train_fetch(0, train_idx)[0])
    opt_state, constrain_fn = svi_init(rng_init, (sample_batch,), (sample_batch,), params)

    @jit
    def epoch_train(opt_state, rng):
        def body_fn(i, val):
            loss_sum, opt_state, rng = val
            rng, rng_binarize = random.split(rng)
            batch = binarize(rng_binarize, train_fetch(i, train_idx)[0])
            loss, opt_state, rng = svi_update(i, rng, opt_state, (batch,), (batch,),)
            loss_sum += loss
            return loss_sum, opt_state, rng

        return lax.fori_loop(0, num_train, body_fn, (0., opt_state, rng))

    @jit
    def eval_test(opt_state, rng):
        def body_fun(i, val):
            loss_sum, rng = val
            rng, rng_binarize, rng_eval = random.split(rng, 3)
            batch = binarize(rng_binarize, test_fetch(i, test_idx)[0])
            loss = svi_eval(rng_eval, opt_state, (batch,), (batch,)) / len(batch)
            loss_sum += loss
            return loss_sum, rng

        loss, _ = lax.fori_loop(0, num_test, body_fun, (0., rng))
        loss = loss / num_test
        return loss

    def reconstruct_img(epoch, rng):
        img = test_fetch(0, test_idx)[0][0]
        plt.imsave(os.path.join(RESULTS_DIR, 'original_epoch={}.png'.format(epoch)), img, cmap='gray')
        rng_binarize, rng_sample = random.split(rng)
        test_sample = binarize(rng_binarize, img)
        params = get_params(opt_state)
        z_mean, z_var = encode(params['encoder'], test_sample.reshape([1, -1]))
        z = dist.Normal(z_mean, z_var).sample(rng_sample)
        img_loc = decode(params['decoder'], z).reshape([28, 28])
        plt.imsave(os.path.join(RESULTS_DIR, 'recons_epoch={}.png'.format(epoch)), img_loc, cmap='gray')

    for i in range(args.num_epochs):
        t_start = time.time()
        num_train, train_idx = train_init()
        _, opt_state, rng = epoch_train(opt_state, rng)
        rng, rng_test, rng_reconstruct = random.split(rng, 3)
        num_test, test_idx = test_init()
        test_loss = eval_test(opt_state, rng_test)
        reconstruct_img(i, rng_reconstruct)
        print("Epoch {}: loss = {} ({:.2f} s.)".format(i, test_loss, time.time() - t_start))