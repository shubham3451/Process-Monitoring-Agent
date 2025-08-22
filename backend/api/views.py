import base64
import gzip
import json
from datetime import datetime
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .authentication import AgentAPIKeyAuthentication
from .models import Host, Snapshot, Process
from .serializers import SnapshotSerializer, HostSerializer, HistoricalProcessSerializer
from .consumers import broadcast_snapshot
from rest_framework.pagination import PageNumberPagination


class IngestAPIView(APIView):
    """
    POST /api/ingest/
    Expects JSON payload: { "payload": "<base64(gzip(JSON snapshot))>" }
    Or accept direct JSON snapshot (uncompressed) if 'payload' not provided.

    """

    authentication_classes = [AgentAPIKeyAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
          Accept two forms:
          1) compressed: {"payload": "<base64...>"}
          2) direct JSON snapshot: {"hostname":..., "snapshot_time":..., "processes":[...]}

        """
        try:
            data = request.data
            snapshots = []

            if isinstance(data, dict) and "payload" in data:
                b64 = data["payload"]
                try:
                    raw = base64.b64decode(b64)
                    decompressed = gzip.decompress(raw)
                    parsed = json.loads(decompressed.decode("utf-8"))
                except Exception as e:
                    return Response({"detail": f"Failed to decode payload: {e}"}
                                    , status=status.HTTP_400_BAD_REQUEST)

                if isinstance(parsed, list):
                    snapshots = parsed
                elif isinstance(parsed, dict):
                    if "snapshots" in parsed and isinstance(parsed["snapshots"], list):
                        snapshots = parsed["snapshots"]
                    else:
                        snapshots = [parsed]
                else:
                    return Response({"detail": "Unsupported payload content"},
                                     status=status.HTTP_400_BAD_REQUEST)

            elif isinstance(data, dict):
                if "snapshot" in data and isinstance(data["snapshot"], list):
                    snapshots = data["snapshot"]
                elif "hostdetails" in data and "snapshot_time" in data:
                    snapshots = [data]
                else:
                    return Response({"detail": "Invalid body"},
                                     status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"detail": "Unsupported body"},
                                 status=status.HTTP_400_BAD_REQUEST)

            created = []
            with transaction.atomic():
                for snap in snapshots:
                    host_data = snap.get("hostdetails", {})
                    hostname = host_data.get("hostname")
                    snapshot_time = snap.get("snapshot_time")
                    processes = snap.get("processes", [])

                    if not hostname or not snapshot_time:
                        continue

                    host, _ = Host.objects.get_or_create(hostname=hostname)
                    serializer = HostSerializer(host, data=host_data, partial=True)
                    if not serializer.is_valid():
                        print(f"Invalid host data: {serializer.errors}")
                       # raise ValueError(f"invalid data, {serializer.errors}")
                        continue
                    serializer.save()


                    snap_dt = None
                    try:
                        snap_dt = parse_datetime(snapshot_time)
                    except Exception:
                        snap_dt = None
                    if snap_dt is None:
                        try:
                            snap_dt = datetime.fromisoformat(snapshot_time)
                        except Exception:
                            snap_dt = timezone.now()

                    snap_obj = Snapshot.objects.create(host=host, snapshot_time=snap_dt)

                    proc_objs = []
                    for p in processes:
                        try:
                            proc_objs.append(Process(
                                snapshot=snap_obj,
                                pid=int(p.get("pid", 0)),
                                ppid=int(p.get("ppid", 0)),
                                name=str(p.get("name", ""))[:512],
                                cpu_percent=float(p.get("cpu_percent", p.get("cpu", 0.0))),
                                rss_bytes=int(p.get("rss_bytes", p.get("memory_rss", 0))),
                            ))
                        except Exception:
                            continue

                    if proc_objs:
                        Process.objects.bulk_create(proc_objs, batch_size=500)

                    created.append({"snapshot_id": snap_obj.id, "hostname": host.hostname})

                    try:
                        broadcast_snapshot(snap_obj.id, host.hostname, snap_obj.snapshot_time.isoformat())
                    except Exception:
                        pass

            return Response({"created": created}, 
                            status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"detail": str(e)}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class HostDetailAPIView(APIView):
    """
    GET /hosts/<hostname>/
    Returns host details for the given hostname.
    """
    permission_classes = [AllowAny]

    def get(self, request, hostname, *args, **kwargs):
        """
        Retrieves host details for the given hostname.
        """
        host = get_object_or_404(Host, hostname=hostname)
        serializer = HostSerializer(host)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LatestSnapshotAPIView(APIView):
    """
    GET /hosts/<hostname>/latest/
    Returns the latest snapshot of a host, including processes.
    """
    permission_classes = [AllowAny]

    def get(self, request, hostname, *args, **kwargs):
        """
        Retrieves the most recent snapshot for the given hostname.
        """
        host = get_object_or_404(Host, hostname=hostname)
        snap = host.snapshots.prefetch_related("processes").first()
        if not snap:
            return Response({"detail": "No snapshots"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SnapshotSerializer(snap)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HistoricalProcessesPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = "page_size"
    max_page_size = 100

class HistoricalProcessesAPIView(APIView):
    """
    GET /hosts/<hostname>/historical-processes/
    Returns paginated snapshot records (with processes) for a host.
    """

    permission_classes = [AllowAny]

    def get(self, request, hostname, *args, **kwargs):
        host = get_object_or_404(Host, hostname=hostname)

        snapshots = Snapshot.objects.filter(host=host).prefetch_related("processes").order_by("-snapshot_time")

        start = request.query_params.get("start")
        end = request.query_params.get("end")
        if start:
            start_dt = parse_datetime(start)
            if start_dt:
                snapshots = snapshots.filter(snapshot_time__gte=start_dt)
        if end:
            end_dt = parse_datetime(end)
            if end_dt:
                snapshots = snapshots.filter(snapshot_time__lte=end_dt)

        paginator = HistoricalProcessesPagination()
        page = paginator.paginate_queryset(snapshots, request)
        serializer = SnapshotSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


