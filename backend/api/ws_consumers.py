import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class HostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.hostname = self.scope["url_route"]["kwargs"].get("hostname")
        self.group_name = f"host_{self.hostname}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            payload = json.loads(text_data) if text_data else {}
        except Exception:
            payload = {}

        if payload.get("action") == "latest":
            snap = await database_sync_to_async(self._get_latest_snapshot)()
            if snap:
                await self.send(
                    text_data=json.dumps({"type": "snapshot", "data": snap})
                )

    def _get_latest_snapshot(self):
        from .models import Host
        from .serializers import SnapshotSerializer
        try:
            host = Host.objects.get(hostname=self.hostname)
            snap = host.snapshots.prefetch_related("processes").first()
            if not snap:
                return None
            return SnapshotSerializer(snap).data
        except Host.DoesNotExist:
            return None

    async def snapshot_created(self, event):
        snapshot_id = event.get("snapshot_id")
        snap = await database_sync_to_async(self._get_snapshot_by_id)(snapshot_id)
        if snap:
            await self.send(
                text_data=json.dumps({"type": "snapshot", "data": snap})
            )

    def _get_snapshot_by_id(self, snapshot_id):
        from .models import Snapshot
        from .serializers import SnapshotSerializer
        try:
            snap = (
                Snapshot.objects.select_related("host")
                .prefetch_related("processes")
                .get(pk=snapshot_id)
            )
            return SnapshotSerializer(snap).data
        except Snapshot.DoesNotExist:
            return None
