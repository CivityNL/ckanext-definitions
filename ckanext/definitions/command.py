import ckanext.definitions.model.definition as definitions_model
import click


def get_commands():
    return [definitions]


@click.group()
def definitions():
    pass


@definitions.command()
def initdb():
    definitions_model.setup()
    click.secho(u"DB tables created", fg=u"green")
