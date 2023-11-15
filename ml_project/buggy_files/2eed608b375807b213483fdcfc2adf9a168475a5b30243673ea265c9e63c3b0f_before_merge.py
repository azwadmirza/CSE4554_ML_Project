    def sum_sample_counts(self):
        """ Sum counts across all samples for kraken data """

        # Sum the percentages for each taxa across all samples
        # Allows us to pick top-5 for each rank
        # Use percentages instead of counts so that deeply-sequences samples
        # are not unfairly over-represented
        for s_name, data in self.kraken_raw_data.items():
            total_guess_count = None
            for row in data:

                # Convenience vars that are easier to read
                rank_code = row["rank_code"]
                classif = row["classif"]

                # Skip anything that doesn't exactly fit a tax rank level
                if row["rank_code"] == "-" or any(c.isdigit() for c in row["rank_code"]):
                    continue

                # Calculate the total read count using percentages
                # We use either unclassified or the first domain encountered, to try to use the largest proportion of reads = most accurate guess
                if rank_code == "U" or (rank_code == "D" and row["counts_rooted"] > total_guess_count):
                    self.kraken_sample_total_readcounts[s_name] = round(
                        float(row["counts_rooted"]) / (row["percent"] / 100.0)
                    )
                    total_guess_count = row["counts_rooted"]

                if rank_code not in self.kraken_total_pct:
                    self.kraken_total_pct[rank_code] = dict()
                    self.kraken_total_counts[rank_code] = dict()

                if classif not in self.kraken_total_pct[rank_code]:
                    self.kraken_total_pct[rank_code][classif] = 0
                    self.kraken_total_counts[rank_code][classif] = 0
                self.kraken_total_pct[rank_code][classif] += row["percent"]
                self.kraken_total_counts[rank_code][classif] += row["counts_rooted"]