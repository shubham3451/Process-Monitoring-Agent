from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def broadcast_snapshot(snapshot_id, hostname, snapshot_time):
    """
    Sends a lightweight event to the host group; consumers can fetch
    details if needed or we can send full payload.
    
    """

    layer = get_channel_layer()
    payload = {
        "type": "snapshot_created",
        "snapshot_id": snapshot_id,
        "hostname": hostname,
        "snapshot_time": snapshot_time,
    }
    group_name = f"host_{hostname}"
    async_to_sync(layer.group_send)(group_name, payload)

