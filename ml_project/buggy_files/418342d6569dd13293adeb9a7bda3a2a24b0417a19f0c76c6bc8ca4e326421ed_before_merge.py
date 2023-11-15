def _yield_sampler_checks(name, Estimator):
    yield check_target_type
    yield check_samplers_one_label
    yield check_samplers_fit
    yield check_samplers_fit_resample
    yield check_samplers_sampling_strategy_fit_resample
    yield check_samplers_sparse
    yield check_samplers_pandas
    yield check_samplers_multiclass_ova
    yield check_samplers_preserve_dtype
    yield check_samplers_sample_indices