from asgiref.sync import async_to_sync
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from draw.models import Debate
from utils.consumers import TournamentConsumer, WSSuperUserRequiredMixin

from .models import PreformedPanel


class AllocationConsumer(TournamentConsumer, WSSuperUserRequiredMixin):
    """Abstract base class for receiving updates to debates and panels,
    making the modifications, and re-broadcasting them. This intent is that the
    WS provides a dict of objects, which in turn have a dict of objects that
    can be updated directly and the original object returned. This avoids
    having to serialise/re-serialise objects that creates many more queries"""
    pass

    def receive_json(self, content):
        # Retrieve either the debates or panels
        print("AllocationConsumer receieved", content)
        json_objects = content['debatesOrPanels']
        try:
            debates_or_panels = self.get_objects(json_objects.keys())
        except ObjectDoesNotExist:
            msg = _("TODO")
            self.send_error(_("TODO"), msg, content)

        # Make and save the change to the objects based on the provided change
        # TODO: these should be a bulk update operation (F expression?) if they
        # are ever used to update a non trivial amount of objects
        for object_id, object_changes in json_objects.items():
            debate_or_panel = debates_or_panels.get(pk=int(object_id))
            for attribute, value in object_changes.items():
                setattr(debate_or_panel, attribute, value)

            debate_or_panel.save()

        # Re-Broadcast initial payload to confirm the change to websockets
        async_to_sync(self.channel_layer.group_send)(
            self.group_name(), {
                'type': 'broadcast_checkin',
                'content': json_objects
            }
        )

    def broadcast_checkin(self, event):
        self.send_json(event['content'])


class DebateEditConsumer(AllocationConsumer):

    group_prefix = 'debates'

    def get_objects(self, ids):
        return Debate.objects.filter(id__in=ids)


class PanelEditConsumer(AllocationConsumer):

    group_prefix = 'panels'

    def get_objects(self, ids):
        return PreformedPanel.objects.filter(id__in=ids)
