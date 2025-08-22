from rest_framework import serializers
from .models import Host, Snapshot, Process

class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ["pid", "ppid", "name", "cpu_percent", "rss_bytes"]



class SnapshotSerializer(serializers.ModelSerializer):
    host = serializers.CharField(source="host.hostname")
    processes = ProcessSerializer(many=True)

    class Meta:
        model = Snapshot
        fields = ["id", "host", "snapshot_time", "processes", "created_at"]




class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = "__all__"
        extra_kwargs = {
            "hostname": {"validators": []}
        }


class HistoricalProcessSerializer(serializers.ModelSerializer):
    snapshot_time = serializers.DateTimeField(source="snapshot.snapshot_time")
    host = serializers.CharField(source="snapshot.host.hostname")

    class Meta:
        model = Process
        fields = ["pid", "ppid", "name", "cpu_percent", "rss_bytes", "snapshot_time", "host"]
