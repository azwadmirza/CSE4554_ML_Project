    def predict(self, infile_name, outfile_name):
        """Make predictions on the given data, and output predicted scores to a file.
        
        Args:
            infile_name (str): Input file name, format is same as train/val/test file.
            outfile_name (str): Output file name, each line is the predict score.

        Returns:
            obj: An instance of self.
        """
        load_sess = self.sess
        with tf.gfile.GFile(outfile_name, "w") as wt:
            for batch_data_input, _, _ in self.iterator.load_data_from_file(infile_name):
                step_pred = self.infer(load_sess, batch_data_input)
                step_pred = np.reshape(step_pred, -1)
                wt.write("\n".join(map(str, step_pred)))
                # line break after each batch.
                wt.write("\n")
        return self