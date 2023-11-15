def pend_benchmark_odeint():
  _, _ = benchmark_odeint(pend, (np.pi - 0.1, 0.0), np.linspace(0., 10., 101),
                          0.25, 9.8)