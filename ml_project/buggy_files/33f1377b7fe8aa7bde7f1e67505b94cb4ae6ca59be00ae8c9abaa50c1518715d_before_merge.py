    def summary(self):
        """Prints a summary of the decomposition and demixing parameters
         to the stdout
        """
        summary_str = (
            "Decomposition parameters:\n"
            "-------------------------\n\n" +
            ("Decomposition algorithm : \t%s\n" %
                self.decomposition_algorithm) +
            ("Poissonian noise normalization : %s\n" %
                self.poissonian_noise_normalized) +
            ("Output dimension : %s\n" % self.output_dimension) +
            ("Centre : %s" % self.centre))
        if self.bss_algorithm is not None:
            summary_str += (
                "\n\nDemixing parameters:\n"
                "------------------------\n" +
                ("BSS algorithm : %s" % self.bss_algorithm) +
                ("Number of components : %i" % len(self.unmixing_matrix)))
        _logger.info(summary_str)