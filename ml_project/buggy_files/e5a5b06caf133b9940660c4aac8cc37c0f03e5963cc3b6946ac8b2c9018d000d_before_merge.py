def main(args):
    baseball_dataset = pd.read_csv(DATA_URL, "\t")
    train, _, player_names = train_test_split(baseball_dataset)
    at_bats, hits = train[:, 0], train[:, 1]
    nuts_kernel = NUTS(conditioned_model)
    logging.info("Original Dataset:")
    logging.info(baseball_dataset)

    # (1) Full Pooling Model
    posterior_fully_pooled = MCMC(nuts_kernel, num_samples=args.num_samples, warmup_steps=args.warmup_steps) \
        .run(fully_pooled, at_bats, hits)
    logging.info("\nModel: Fully Pooled")
    logging.info("===================")
    logging.info("\nphi:")
    logging.info(summary(posterior_fully_pooled, sites=["phi"], player_names=player_names)["phi"])
    posterior_predictive = TracePredictive(fully_pooled,
                                           posterior_fully_pooled,
                                           num_samples=args.num_samples)
    sample_posterior_predictive(posterior_predictive, baseball_dataset)
    evaluate_log_predictive_density(fully_pooled, posterior_fully_pooled, baseball_dataset)

    # (2) No Pooling Model
    posterior_not_pooled = MCMC(nuts_kernel, num_samples=args.num_samples, warmup_steps=args.warmup_steps) \
        .run(not_pooled, at_bats, hits)
    logging.info("\nModel: Not Pooled")
    logging.info("=================")
    logging.info("\nphi:")
    logging.info(summary(posterior_not_pooled, sites=["phi"], player_names=player_names)["phi"])
    posterior_predictive = TracePredictive(not_pooled,
                                           posterior_not_pooled,
                                           num_samples=args.num_samples)
    sample_posterior_predictive(posterior_predictive, baseball_dataset)
    evaluate_log_predictive_density(not_pooled, posterior_not_pooled, baseball_dataset)

    # (3) Partially Pooled Model
    posterior_partially_pooled = MCMC(nuts_kernel, num_samples=args.num_samples, warmup_steps=args.warmup_steps) \
        .run(partially_pooled, at_bats, hits)
    logging.info("\nModel: Partially Pooled")
    logging.info("=======================")
    logging.info("\nphi:")
    logging.info(summary(posterior_partially_pooled, sites=["phi"],
                         player_names=player_names)["phi"])
    posterior_predictive = TracePredictive(partially_pooled,
                                           posterior_partially_pooled,
                                           num_samples=args.num_samples)
    sample_posterior_predictive(posterior_predictive, baseball_dataset)
    evaluate_log_predictive_density(partially_pooled, posterior_partially_pooled, baseball_dataset)

    # (4) Partially Pooled with Logit Model
    posterior_partially_pooled_with_logit = MCMC(nuts_kernel, num_samples=args.num_samples,
                                                 warmup_steps=args.warmup_steps) \
        .run(partially_pooled_with_logit, at_bats, hits)
    logging.info("\nModel: Partially Pooled with Logit")
    logging.info("==================================")
    logging.info("\nSigmoid(alpha):")
    logging.info(summary(posterior_partially_pooled_with_logit,
                         sites=["alpha"],
                         player_names=player_names,
                         transforms={"alpha": lambda x: 1. / (1 + np.exp(-x))})["alpha"])
    posterior_predictive = TracePredictive(partially_pooled_with_logit,
                                           posterior_partially_pooled_with_logit,
                                           num_samples=args.num_samples)
    sample_posterior_predictive(posterior_predictive, baseball_dataset)
    evaluate_log_predictive_density(partially_pooled_with_logit,
                                    posterior_partially_pooled_with_logit, baseball_dataset)