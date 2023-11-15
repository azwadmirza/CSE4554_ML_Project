    def get_fliers(self, outliers):
        # Filters only the outliers, should "showfliers" be True
        fliers_df = outliers.filter('__{}_outlier'.format(self.colname))

        # If shows fliers, takes the top 1k with highest absolute values
        fliers = (fliers_df
                  .select(F.abs(F.col('`{}`'.format(self.colname))).alias(self.colname))
                  .orderBy(F.desc('`{}`'.format(self.colname)))
                  .limit(1001)
                  .toPandas()[self.colname].values)

        return fliers