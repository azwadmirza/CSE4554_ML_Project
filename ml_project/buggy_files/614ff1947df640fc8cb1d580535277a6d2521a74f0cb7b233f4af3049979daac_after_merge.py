    def general_stats_cols(self):
        """ Add a couple of columns to the General Statistics table """

        # Get top taxa in most specific taxa rank that we have
        top_five = []
        top_rank_code = None
        top_rank_name = None
        for rank_code, rank_name in self.t_ranks.items():
            try:
                sorted_pct = sorted(self.kraken_total_pct[rank_code].items(), key=lambda x: x[1], reverse=True)
                for classif, pct_sum in sorted_pct[:5]:
                    top_five.append(classif)
                top_rank_code = rank_code
                top_rank_name = rank_name
                break
            except KeyError:
                # No species-level data found etc
                pass

        top_one_hkey = "% {}".format(top_five[0])

        # Column headers
        headers = OrderedDict()
        headers[top_one_hkey] = {
            "title": top_one_hkey,
            "description": "Percentage of reads that were the top {} over all samples - {}".format(
                top_rank_name, top_five[0]
            ),
            "suffix": "%",
            "max": 100,
            "scale": "PuBuGn",
        }
        headers["% Top 5"] = {
            "title": "% Top 5 {}".format(top_rank_name),
            "description": "Percentage of reads that were classified by one of the top 5 {} ({})".format(
                top_rank_name, ", ".join(top_five)
            ),
            "suffix": "%",
            "max": 100,
            "scale": "PuBu",
        }
        headers["% Unclassified"] = {
            "title": "% Unclassified",
            "description": "Percentage of reads that were unclassified",
            "suffix": "%",
            "max": 100,
            "scale": "OrRd",
        }

        # Get table data
        tdata = {}
        for s_name, d in self.kraken_raw_data.items():
            tdata[s_name] = {}
            for row in d:
                percent = (row["counts_rooted"] / self.kraken_sample_total_readcounts[s_name]) * 100.0
                if row["rank_code"] == "U":
                    tdata[s_name]["% Unclassified"] = percent
                if row["rank_code"] == top_rank_code and row["classif"] in top_five:
                    tdata[s_name]["% Top 5"] = percent + tdata[s_name].get("% Top 5", 0)
                if row["rank_code"] == top_rank_code and row["classif"] == top_five[0]:
                    tdata[s_name][top_one_hkey] = percent

            if top_one_hkey not in tdata[s_name]:
                tdata[s_name][top_one_hkey] = 0

        self.general_stats_addcols(tdata, headers)