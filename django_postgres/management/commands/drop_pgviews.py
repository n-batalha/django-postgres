from optparse import make_option
import logging

from django.core.management.base import NoArgsCommand
from django.db import models

from django_postgres.view import drop_views


log = logging.getLogger('django_postgres.drop_pgviews')


class Command(NoArgsCommand):
    help = """Drop Postgres views for all installed apps."""
    option_list = NoArgsCommand.option_list + (
        make_option('--force',
                    action='store_true',
                    dest='force',
                    default=False,
                    help="""Automatically drop objects that depend on the view (such as other views)."""),
    )

    def handle_noargs(self, force, **options):
        for module in models.get_apps():
            log.info("Dropping views for %s", module.__name__)
            try:
                for status, view_cls, python_name in drop_views(module, force=force):
                    if status == 'DROPPED':
                        msg = "dropped"
                    elif status == 'NOTEXISTS':
                        msg = "doesn't exist, skipping"
                    log.info("%(python_name)s (%(view_name)s): %(msg)s" % {
                        'python_name': python_name,
                        'view_name': view_cls._meta.db_table,
                        'msg': msg})
            except Exception, exc:
                if not hasattr(exc, 'view_cls'):
                    raise
                log.exception("Error dropping view %s (%r)",
                              exc.python_name,
                              exc.view_cls._meta.db_table)
