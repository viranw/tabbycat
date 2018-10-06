from asgiref.sync import async_to_sync
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from draw.models import Debate
from utils.consumers import TournamentConsumer, WSSuperUserRequiredMixin

from .models import PreformedPanel


class AllocationConsumer(TournamentConsumer, WSSuperUserRequiredMixin):
    """Abstract base class for receiving updates to debates and panels,
    making the modifications, and re-broadcasting them."""
    pass

    def receive_json(self, content):
        # Retrieve either the debates or panels
        ids = [o.id for o in content.debates_or_panels]
        try:
            debates_or_panels = self.get_objects(ids)
        except ObjectDoesNotExist:
            msg = _("TODO")
            self.send_error(_("TODO"), msg, content)

        # Make and save the change to the objects based on the provided change

        # Broadcast the change to the object listening websockets
        async_to_sync(self.channel_layer.group_send)(
            self.group_name(), {
                'type': 'broadcast_checkin',
                'content': debates_or_panels
            }
        )

    def broadcast_checkin(self, event):
        self.send_json(None)


class DebateEditConsumer(AllocationConsumer):

    group_prefix = 'debates'

    def get_objects(self, ids):
        return Debate.objects.get(pk=0)


class PanelEditConsumer(AllocationConsumer):

    group_prefix = 'panels'

    def get_objects(self, ids):
        return PreformedPanel.objects.get(pk=0)
