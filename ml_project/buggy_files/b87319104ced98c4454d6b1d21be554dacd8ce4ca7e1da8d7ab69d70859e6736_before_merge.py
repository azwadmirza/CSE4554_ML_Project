    def from_pipeline(proj_pipeline):
        """Make a Transformer from a PROJ pipeline string.

        https://proj4.org/operations/pipeline.html

        Parameters
        ----------
        proj_pipeline: str
            Projection pipeline string.

        Returns
        -------
        ~Transformer

        """
        transformer = Transformer()
        transformer._transformer = _Transformer.from_pipeline(cstrencode(proj_pipeline))
        return transformer