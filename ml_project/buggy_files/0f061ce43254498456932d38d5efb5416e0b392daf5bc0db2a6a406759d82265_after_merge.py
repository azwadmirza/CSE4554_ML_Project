    def _repr_latex_(self):
        """
        Generate a LaTeX representation of the Qobj instance. Can be used for
        formatted output in ipython notebook.
        """
        s = r'$\text{'
        if self.type in ['oper', 'super']:
            s += ("Quantum object: " +
                  "dims = " + str(self.dims) +
                  ", shape = " + str(self.shape) +
                  ", type = " + self.type +
                  ", isherm = " + str(self._isherm) +
                  (
                      ", superrep = {0.superrep}".format(self)
                      if self.type == "super" and self.superrep != "super"
                      else ""
                  ))
        else:
            s += ("Quantum object: " +
                  "dims = " + str(self.dims) +
                  ", shape = " + str(self.shape) +
                  ", type = " + self.type)

        s += r'}\\[1em]'

        M, N = self.data.shape

        s += r'\begin{pmatrix}'

        def _format_float(value):
            if value == 0.0:
                return "0.0"
            elif abs(value) > 1000.0 or abs(value) < 0.001:
                return ("%.3e" % value).replace("e", r"\times10^{") + "}"
            elif abs(value - int(value)) < 0.001:
                return "%.1f" % value
            else:
                return "%.3f" % value

        def _format_element(m, n, d):
            s = " & " if n > 0 else ""
            if type(d) == str:
                return s + d
            else:
                if abs(np.imag(d)) < 1e-12:
                    return s + _format_float(np.real(d))
                elif abs(np.real(d)) < 1e-12:
                    return s + _format_float(np.imag(d)) + "j"
                else:
                    s_re = _format_float(np.real(d))
                    s_im = _format_float(np.imag(d))
                    if np.imag(d) > 0.0:
                        return (s + "(" + s_re + "+" + s_im + "j)")
                    else:
                        return (s + "(" + s_re + s_im + "j)")

        if M > 10 and N > 10:
            # truncated matrix output
            for m in range(5):
                for n in range(5):
                    s += _format_element(m, n, self.data[m, n])
                s += r' & \cdots'
                for n in range(N - 5, N):
                    s += _format_element(m, n, self.data[m, n])
                s += r'\\'

            for n in range(5):
                s += _format_element(m, n, r'\vdots')
            s += r' & \ddots'
            for n in range(N - 5, N):
                s += _format_element(m, n, r'\vdots')
            s += r'\\'

            for m in range(M - 5, M):
                for n in range(5):
                    s += _format_element(m, n, self.data[m, n])
                s += r' & \cdots'
                for n in range(N - 5, N):
                    s += _format_element(m, n, self.data[m, n])
                s += r'\\'

        elif M > 10 and N == 1:
            # truncated column vector output
            for m in range(5):
                s += _format_element(m, 0, self.data[m, 0])
                s += r'\\'

            s += _format_element(m, 0, r'\vdots')
            s += r'\\'

            for m in range(M - 5, M):
                s += _format_element(m, 0, self.data[m, 0])
                s += r'\\'

        elif M == 1 and N > 10:
            # truncated row vector output
            for n in range(5):
                s += _format_element(0, n, self.data[0, n])
            s += r' & \cdots'
            for n in range(N - 5, N):
                s += _format_element(0, n, self.data[0, n])
            s += r'\\'

        else:
            # full output
            for m in range(M):
                for n in range(N):
                    s += _format_element(m, n, self.data[m, n])
                s += r'\\'

        s += r'\end{pmatrix}$'
        return s