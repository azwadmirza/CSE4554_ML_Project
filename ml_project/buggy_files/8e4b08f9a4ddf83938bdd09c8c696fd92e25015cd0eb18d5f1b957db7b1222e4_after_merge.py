def main_group(
    ctx,
    verbose,
    quiet,
    aws_profile,
    aws_no_sign_requests,
    aws_requester_pays,
    gdal_version,
):
    """Rasterio command line interface.
    """
    verbosity = verbose - quiet
    configure_logging(verbosity)
    ctx.obj = {}
    ctx.obj["verbosity"] = verbosity
    ctx.obj["aws_profile"] = aws_profile
    envopts = {"CPL_DEBUG": (verbosity > 2)}
    if aws_profile or aws_no_sign_requests or aws_requester_pays:
        ctx.obj["env"] = rasterio.Env(
            session=AWSSession(
                profile_name=aws_profile,
                aws_unsigned=aws_no_sign_requests,
                requester_pays=aws_requester_pays,
            ), **envopts)
    else:
        ctx.obj["env"] = rasterio.Env(**envopts)