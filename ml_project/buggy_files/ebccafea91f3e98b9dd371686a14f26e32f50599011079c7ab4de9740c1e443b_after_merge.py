    def upper_bound(self) -> tf.Tensor:
        """
        Upper bound for the sparse GP regression marginal likelihood.  Note that
        the same inducing points are used for calculating the upper bound, as are
        used for computing the likelihood approximation. This may not lead to the
        best upper bound. The upper bound can be tightened by optimising Z, just
        like the lower bound. This is especially important in FITC, as FITC is
        known to produce poor inducing point locations. An optimisable upper bound
        can be found in https://github.com/markvdw/gp_upper.

        The key reference is

        ::

          @misc{titsias_2014,
            title={Variational Inference for Gaussian and Determinantal Point Processes},
            url={http://www2.aueb.gr/users/mtitsias/papers/titsiasNipsVar14.pdf},
            publisher={Workshop on Advances in Variational Inference (NIPS 2014)},
            author={Titsias, Michalis K.},
            year={2014},
            month={Dec}
          }

        The key quantity, the trace term, can be computed via

        >>> _, v = conditionals.conditional(X, model.inducing_variable.Z, model.kernel,
        ...                                 np.zeros((model.inducing_variable.num_inducing, 1)))

        which computes each individual element of the trace term.
        """
        X_data, Y_data = self.data
        num_data = to_default_float(tf.shape(Y_data)[0])

        Kdiag = self.kernel(X_data, full_cov=False)
        kuu = Kuu(self.inducing_variable, self.kernel, jitter=default_jitter())
        kuf = Kuf(self.inducing_variable, self.kernel, X_data)

        I = tf.eye(tf.shape(kuu)[0], dtype=default_float())

        L = tf.linalg.cholesky(kuu)
        A = tf.linalg.triangular_solve(L, kuf, lower=True)
        AAT = tf.linalg.matmul(A, A, transpose_b=True)
        B = I + AAT / self.likelihood.variance
        LB = tf.linalg.cholesky(B)

        # Using the Trace bound, from Titsias' presentation
        c = tf.reduce_sum(Kdiag) - tf.reduce_sum(tf.square(A))

        # Alternative bound on max eigenval:
        corrected_noise = self.likelihood.variance + c

        const = -0.5 * num_data * tf.math.log(2 * np.pi * self.likelihood.variance)
        logdet = -tf.reduce_sum(tf.math.log(tf.linalg.diag_part(LB)))

        err = Y_data - self.mean_function(X_data)
        LC = tf.linalg.cholesky(I + AAT / corrected_noise)
        v = tf.linalg.triangular_solve(LC, tf.linalg.matmul(A, err) / corrected_noise, lower=True)
        quad = -0.5 * tf.reduce_sum(tf.square(err)) / corrected_noise + 0.5 * tf.reduce_sum(
            tf.square(v)
        )

        return const + logdet + quad