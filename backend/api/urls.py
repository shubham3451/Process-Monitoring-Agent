from django.urls import path
from .views import (
                    IngestAPIView,
                    LatestSnapshotAPIView,
                    HostDetailAPIView,
                    HistoricalProcessesAPIView
                    )

urlpatterns = [
    path("ingest/", IngestAPIView.as_view(), name="ingest"),
    path("hosts/<str:hostname>/latest/", LatestSnapshotAPIView.as_view(), name="latest_snapshot"),
    path("hosts/<str:hostname>/", HostDetailAPIView.as_view(), name="host_detail"),
    path("history/<str:hostname>/", HistoricalProcessesAPIView.as_view(), name="historical_processes"),

]
