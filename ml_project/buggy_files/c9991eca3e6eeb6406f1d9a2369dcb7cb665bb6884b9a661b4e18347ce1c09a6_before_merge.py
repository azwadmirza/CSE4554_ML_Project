    def finalizetempoutputfile(self, options, outputfile, fulloutputpath):
        """Write the temp outputfile to its final destination."""
        outputfile.reset()
        outputstring = outputfile.read()
        outputfile = self.openoutputfile(options, fulloutputpath)
        outputfile.write(outputstring)
        outputfile.close()