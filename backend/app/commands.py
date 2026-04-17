import click
from flask import current_app
from flask.cli import with_appcontext

from .extensions import db
from .models import AdminUser


@click.command("set-owner")
@click.argument("email")
@with_appcontext
def set_owner_command(email: str) -> None:
    """Promote the AdminUser with EMAIL to sole owner.

    Clears any existing owner in the same transaction, so this is safe to run
    whether there are zero, one, or (hypothetically) more current owners. The
    target must already exist as an admin — create them via the Officers UI
    first, or (for first-owner bootstrap) insert the admin_users row manually.
    """
    target = AdminUser.query.filter(db.func.lower(AdminUser.email) == email.lower()).first()
    if target is None:
        raise click.ClickException(f"No admin_users row for email '{email}'. Insert one first.")

    current_owners = AdminUser.query.filter_by(is_owner=True).all()
    for owner in current_owners:
        if owner.id != target.id:
            owner.is_owner = False
    db.session.flush()

    target.is_owner = True
    db.session.commit()
    click.echo(f"Set owner: {target.email} (id={target.id}).")


def register_commands(app) -> None:
    app.cli.add_command(set_owner_command)
