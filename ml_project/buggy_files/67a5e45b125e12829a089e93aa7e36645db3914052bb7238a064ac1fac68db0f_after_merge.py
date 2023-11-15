    def update(self, actor, session):
        if self.id and self.id != actor.get('ids').get('trakt'):
            raise Exception('Tried to update db actors with different actor data')
        elif not self.id:
            self.id = actor.get('ids').get('trakt')
        self.name = actor.get('name')
        ids = actor.get('ids')
        self.imdb = ids.get('imdb')
        self.slug = ids.get('slug')
        self.tmdb = ids.get('tmdb')
        self.biography = actor.get('biography')
        if actor.get('birthday'):
            self.birthday = dateutil_parse(actor.get('birthday'))
        if actor.get('death'):
            self.death = dateutil_parse(actor.get('death'))
        self.homepage = actor.get('homepage')
        if actor.get('images'):
            set_image_attributes(self, actor)