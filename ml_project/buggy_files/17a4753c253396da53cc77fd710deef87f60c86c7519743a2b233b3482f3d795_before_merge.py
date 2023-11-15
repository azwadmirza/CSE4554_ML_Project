def get_local_urls():
    from conda.models.channel import get_conda_build_local_url
    return get_conda_build_local_url() or []