    def normalize(single_inpt):
        if abs(single_inpt) < 1e-14:
            return '0'
        val = single_inpt / np.pi
        if output in ['text', 'qasm']:
            pi = 'pi'
        elif output == 'latex':
            pi = '\\pi'
        elif output == 'mpl':
            pi = '$\\pi$'
        else:
            raise QiskitError('pi_check parameter output should be text, '
                              'latex, mpl, or qasm.')
        if abs(val) >= 1 - eps:
            if abs(abs(val) - abs(round(val))) < eps:
                val = int(round(val))
                if val == 1:
                    str_out = '{}'.format(pi)
                elif val == -1:
                    str_out = '-{}'.format(pi)
                else:
                    if output == 'qasm':
                        str_out = '{}*{}'.format(val, pi)
                    else:
                        str_out = '{}{}'.format(val, pi)
                return str_out

        val = np.pi / single_inpt
        if abs(abs(val) - abs(round(val))) < eps:
            val = int(round(val))
            if val > 0:
                if output == 'latex':
                    str_out = '\\frac{%s}{%s}' % (pi, abs(val))
                else:
                    str_out = '{}/{}'.format(pi, val)
            else:
                if output == 'latex':
                    str_out = '\\frac{-%s}{%s}' % (pi, abs(val))
                else:
                    str_out = '-{}/{}'.format(pi, abs(val))
            return str_out

        # Look for all fracs in 8
        abs_val = abs(single_inpt)
        frac = np.where(np.abs(abs_val - FRAC_MESH) < 1e-8)
        if frac[0].shape[0]:
            numer = int(frac[1][0]) + 1
            denom = int(frac[0][0]) + 1
            if single_inpt < 0:
                numer *= -1

            if numer == 1 and denom == 1:
                str_out = '{}'.format(pi)
            elif numer == -1 and denom == 1:
                str_out = '-{}'.format(pi)
            elif numer == 1:
                if output == 'latex':
                    str_out = '\\frac{%s}{%s}' % (pi, denom)
                else:
                    str_out = '{}/{}'.format(pi, denom)
            elif numer == -1:
                if output == 'latex':
                    str_out = '\\frac{-%s}{%s}' % (pi, denom)
                else:
                    str_out = '-{}/{}'.format(pi, denom)
            elif denom == 1:
                if output == 'latex':
                    str_out = '\\frac{%s}{%s}' % (numer, pi)
                else:
                    str_out = '{}/{}'.format(numer, pi)
            else:
                if output == 'latex':
                    str_out = '\\frac{%s%s}{%s}' % (numer, pi, denom)
                elif output == 'qasm':
                    str_out = '{}*{}/{}'.format(numer, pi, denom)
                else:
                    str_out = '{}{}/{}'.format(numer, pi, denom)

            return str_out
        # nothing found
        str_out = '%.{}g'.format(ndigits) % single_inpt
        return str_out