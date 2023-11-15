def load_default_model(session):
    element_factory = session.get_service("element_factory")
    element_factory.flush()
    with element_factory.block_events():
        model = element_factory.create(UML.Package)
        model.name = gettext("New model")
        diagram = element_factory.create(UML.Diagram)
        diagram.package = model
        diagram.name = gettext("main")
    element_factory.model_ready()