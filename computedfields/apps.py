from django.apps import AppConfig
import sys
from django.db.models.signals import class_prepared
from .resolver import BOOT_RESOLVER


class ComputedfieldsConfig(AppConfig):
    name = 'computedfields'

    def __init__(self, *args, **kwargs):
        super(ComputedfieldsConfig, self).__init__(*args, **kwargs)

        # register bootup model discovery
        self.track_bootmodels = False
        for token in ('makemigrations', 'migrate', 'help'):
            if token in sys.argv:  # pragma: no cover
                break
        else:
            class_prepared.connect(BOOT_RESOLVER.add_model)
            self.track_bootmodels = True


    def ready(self):
        # disconnect model discovery to avoid resolver issues with models created later at runtime
        if self.track_bootmodels:
            class_prepared.disconnect(BOOT_RESOLVER.add_model)

        # do not run graph reduction in migrations
        for token in ('makemigrations', 'migrate', 'help', 'rendergraph', 'createmap'):
            if token in sys.argv:  # pragma: no cover
                return

        # normal startup
        BOOT_RESOLVER.initialize()

        # connect signals
        from computedfields.handlers import (
            postsave_handler, predelete_handler, postdelete_handler, m2m_handler, get_old_handler)
        from django.db.models.signals import post_save, m2m_changed, pre_delete, post_delete, pre_save

        pre_save.connect(
            get_old_handler, sender=None, weak=False, dispatch_uid='COMP_FIELD_PRESAVE')
        post_save.connect(
            postsave_handler, sender=None, weak=False, dispatch_uid='COMP_FIELD')
        pre_delete.connect(
            predelete_handler, sender=None, weak=False, dispatch_uid='COMP_FIELD_PREDELETE')
        post_delete.connect(
            postdelete_handler, sender=None, weak=False, dispatch_uid='COMP_FIELD_POSTDELETE')
        m2m_changed.connect(
            m2m_handler, sender=None, weak=False, dispatch_uid='COMP_FIELD_M2M')
