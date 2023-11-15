    def measure_homodyne(self, phi, mode, select=None, **kwargs):
        """
        Performs a homodyne measurement on a mode.
        """
        m_omega_over_hbar = 1 / self._hbar

        # Make sure the state is mixed for reduced density matrix
        if self._pure:
            state = ops.mix(self._state, self._num_modes)
        else:
            state = self._state

        if select is not None:
            meas_result = select
            if isinstance(meas_result, numbers.Number):
                homodyne_sample = float(meas_result)
            else:
                raise TypeError("Selected measurement result must be of numeric type.")
        else:
            # Compute reduced density matrix
            unmeasured = [i for i in range(self._num_modes) if not i == mode]
            reduced = ops.partial_trace(state, self._num_modes, unmeasured)

            # Rotate to measurement basis
            reduced = self.apply_gate_BLAS(
                ops.phase(-phi, self._trunc), [0], state=reduced, pure=False, n=1
            )

            # Create pdf. Same as tf implementation, but using
            # the recursive relation H_0(x) = 1, H_1(x) = 2x, H_{n+1}(x) = 2xH_n(x) - 2nH_{n-1}(x)
            q_mag = kwargs.get("max", 10)
            num_bins = kwargs.get("num_bins", 100000)

            q_tensor, Hvals = ops.hermiteVals(q_mag, num_bins, m_omega_over_hbar, self._trunc)
            H_matrix = np.zeros((self._trunc, self._trunc, num_bins))
            for n, m in product(range(self._trunc), repeat=2):
                H_matrix[n][m] = 1 / sqrt(2 ** n * bang(n) * 2 ** m * bang(m)) * Hvals[n] * Hvals[m]
            H_terms = np.expand_dims(reduced, -1) * np.expand_dims(H_matrix, 0)
            rho_dist = (
                np.sum(H_terms, axis=(1, 2))
                * (m_omega_over_hbar / pi) ** 0.5
                * np.exp(-m_omega_over_hbar * q_tensor ** 2)
                * (q_tensor[1] - q_tensor[0])
            )  # Delta_q for normalization (only works if the bins are equally spaced)

            # Sample from rho_dist. This is a bit different from tensorflow due to how
            # numpy treats multinomial sampling. In particular, numpy returns a
            # histogram of the samples whereas tensorflow gives the list of samples.
            # Numpy also does not use the log probabilities
            probs = rho_dist.flatten().real
            probs /= np.sum(probs)
            sample_hist = np.random.multinomial(1, probs)
            sample_idx = list(sample_hist).index(1)
            homodyne_sample = q_tensor[sample_idx]

        # Project remaining modes into the conditional state
        inf_squeezed_vac = np.array(
            [
                (-0.5) ** (n // 2) * sqrt(bang(n)) / bang(n // 2) if n % 2 == 0 else 0.0 + 0.0j
                for n in range(self._trunc)
            ],
            dtype=ops.def_type,
        )
        alpha = homodyne_sample * sqrt(m_omega_over_hbar / 2)

        composed = np.dot(ops.phase(phi, self._trunc), ops.displacement(alpha, self._trunc))
        eigenstate = self.apply_gate_BLAS(composed, [0], state=inf_squeezed_vac, pure=True, n=1)

        vac_state = np.array(
            [1.0 + 0.0j if i == 0 else 0.0 + 0.0j for i in range(self._trunc)], dtype=ops.def_type
        )
        projector = np.outer(vac_state, eigenstate.conj())

        self._state = self.apply_gate_BLAS(projector, [mode])

        # Normalize
        self._state = self._state / self.norm()

        return homodyne_sample