    def random_split_ConcatDataset(self, ds, lengths):
        """
        Roughly split a Concatdataset into non-overlapping new datasets of given lengths.
        Samples inside Concatdataset should already be shuffled

        Arguments:
            ds (Dataset): Dataset to be split
            lengths (sequence): lengths of splits to be produced
        """
        if sum(lengths) != len(ds):
            raise ValueError("Sum of input lengths does not equal the length of the input dataset!")

        idx_dataset = np.where(np.array(ds.cumulative_sizes) > lengths[0])[0][0]

        train = ConcatDataset(ds.datasets[:idx_dataset])
        test = ConcatDataset(ds.datasets[idx_dataset:])
        return train, test