    def index():
        unstarred = []
        starred = []

        # Long SQLAlchemy statements look best when formatted according to
        # the Pocoo style guide, IMHO:
        # http://www.pocoo.org/internal/styleguide/
        sources = Source.query.filter_by(pending=False) \
                              .order_by(Source.last_updated.desc()) \
                              .all()
        for source in sources:
            star = SourceStar.query.filter_by(source_id=source.id).first()
            if star and star.starred:
                starred.append(source)
            else:
                unstarred.append(source)
            source.num_unread = len(
                Submission.query.filter_by(source_id=source.id,
                                           downloaded=False).all())

        return render_template('index.html',
                               unstarred=unstarred,
                               starred=starred)