def _parse_image_meta(image=None, detail=False):
    ret = None

    if image and 'Error' in image:
        ret = image
    elif image and 'manifest' in image:
        name = image['manifest']['name']
        version = image['manifest']['version']
        os = image['manifest']['os']
        description = image['manifest']['description']
        published = image['manifest']['published_at']
        source = image['source']
        if image['manifest']['name'] == 'docker-layer':
            # NOTE: skip docker-layer unless it has a docker:repo and docker:tag
            name = None
            docker_repo = None
            docker_tag = None
            for tag in image['manifest']['tags']:
                if tag.startswith('docker:tag:') and image['manifest']['tags'][tag]:
                    docker_tag = tag.split(':')[-1]
                elif tag == 'docker:repo':
                    docker_repo = image['manifest']['tags'][tag]

            if docker_repo and docker_tag:
                name = '{}:{}'.format(docker_repo, docker_tag)
                description = 'Docker image imported from {repo}:{tag} on {date}.'.format(
                    repo=docker_repo,
                    tag=docker_tag,
                    date=published,
                )

        if name and detail:
            ret = {
              'name': name,
              'version': version,
              'os': os,
              'description': description,
              'published': published,
              'source': source,
            }
        elif name:
            ret = '{name}@{version} [{published}]'.format(
                name=name,
                version=version,
                published=published,
            )

    return ret