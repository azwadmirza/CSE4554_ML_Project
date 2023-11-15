    def __init__(self, session=None, aws_unsigned=False, profile_name=None,
                 session_class=AWSSession, **options):
        """Create a new GDAL/AWS environment.

        Note: this class is a context manager. GDAL isn't configured
        until the context is entered via `with rasterio.Env():`

        Parameters
        ----------
        session : optional
            A Session object.
        aws_unsigned : bool, optional
            Do not sign cloud requests.
        profile_name : str, optional
            A shared credentials profile name, as per boto3.
        session_class : Session, optional
            A sub-class of Session.
        **options : optional
            A mapping of GDAL configuration options, e.g.,
            `CPL_DEBUG=True, CHECK_WITH_INVERT_PROJ=False`.

        Returns
        -------
        Env

        Notes
        -----
        We raise EnvError if the GDAL config options
        AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY are given. AWS
        credentials are handled exclusively by boto3.

        Examples
        --------

        >>> with Env(CPL_DEBUG=True, CPL_CURL_VERBOSE=True):
        ...     with rasterio.open("https://example.com/a.tif") as src:
        ...         print(src.profile)

        For access to secured cloud resources, a Rasterio Session or a
        foreign session object may be passed to the constructor.

        >>> import boto3
        >>> from rasterio.session import AWSSession
        >>> boto3_session = boto3.Session(...)
        >>> with Env(AWSSession(boto3_session)):
        ...     with rasterio.open("s3://mybucket/a.tif") as src:
        ...         print(src.profile)

        """
        aws_access_key_id = options.pop('aws_access_key_id', None)
        # Before 1.0, Rasterio only supported AWS. We will special
        # case AWS in 1.0.x. TODO: warn deprecation in 1.1.
        if aws_access_key_id:
            warnings.warn(
                "Passing abstract session keyword arguments is deprecated. "
                "Pass a Rasterio AWSSession object instead.",
                RasterioDeprecationWarning
            )

        aws_secret_access_key = options.pop('aws_secret_access_key', None)
        aws_session_token = options.pop('aws_session_token', None)
        region_name = options.pop('region_name', None)

        if ('AWS_ACCESS_KEY_ID' in options or
                'AWS_SECRET_ACCESS_KEY' in options):
            raise EnvError(
                "GDAL's AWS config options can not be directly set. "
                "AWS credentials are handled exclusively by boto3.")

        if session:
            # Passing a session via keyword argument is the canonical
            # way to configure access to secured cloud resources.
            if not isinstance(session, Session):
                warnings.warn(
                    "Passing a boto3 session is deprecated. Pass a Rasterio "
                    "AWSSession object instead.",
                    RasterioDeprecationWarning
                )
                session = AWSSession(session=session)
            self.session = session
        elif aws_access_key_id or profile_name or aws_unsigned:
            self.session = AWSSession(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
                region_name=region_name,
                profile_name=profile_name,
                aws_unsigned=aws_unsigned)
        elif 'AWS_ACCESS_KEY_ID' in os.environ and 'AWS_SECRET_ACCESS_KEY' in os.environ:
            self.session = AWSSession()
        else:
            self.session = DummySession()

        self.options = options.copy()
        self.context_options = {}