    def _find_strongest_correlation(self, correlations):
        m_max = np.argmax(np.abs(correlations.flatten()))
        i = int(m_max // len(correlations))
        j = int(m_max - i*len(correlations))
        return (i, j)