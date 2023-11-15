def get_local_urls():
    from .models.channel import get_conda_build_local_url
    return get_conda_build_local_url() or []