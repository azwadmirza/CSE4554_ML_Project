    def get_job_result(self, job_id: str) -> Result:
        """Returns the result of a job.

        Args:
            job_id (str): the job ID

        Returns:
            strawberryfields.api.Result: the job result
        """
        path = "/jobs/{}/result".format(job_id)
        response = requests.get(
            self._url(path), headers={"Accept": "application/x-numpy", **self._headers}
        )
        if response.status_code == 200:
            # Read the numpy binary data in the payload into memory
            with io.BytesIO() as buf:
                buf.write(response.content)
                buf.seek(0)

                samples = np.load(buf, allow_pickle=False)

                if np.issubdtype(samples.dtype, np.integer):
                    # Samples represent photon numbers.
                    # Convert to int64, to avoid unexpected behaviour
                    # when users postprocess these samples.
                    samples = samples.astype(np.int64)

            return Result(samples, is_stateful=False)
        raise RequestFailedError(
            "Failed to get job result: {}".format(self._format_error_message(response))
        )