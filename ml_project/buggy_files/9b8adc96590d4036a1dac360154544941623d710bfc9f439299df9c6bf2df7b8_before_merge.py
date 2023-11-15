def optimal_step_size(last_step,
                      mean_error_ratio,
                      safety=0.9,
                      ifactor=10.0,
                      dfactor=0.2,
                      order=5.0):
  """Compute optimal Runge-Kutta stepsize."""
  mean_error_ratio = np.max(mean_error_ratio)
  dfactor = np.where(mean_error_ratio < 1,
                     1.0,
                     dfactor)

  err_ratio = np.sqrt(mean_error_ratio)
  factor = np.maximum(1.0 / ifactor,
                      np.minimum(err_ratio**(1.0 / order) / safety,
                                 1.0 / dfactor))
  return np.where(mean_error_ratio == 0,
                  last_step * ifactor,
                  last_step / factor,)