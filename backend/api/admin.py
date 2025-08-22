from django.contrib import admin
from .models import Host, Snapshot, Process

@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ("hostname", "created_at")

@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    list_display = ("id", "host", "snapshot_time", "created_at")
    list_filter = ("host",)

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ("pid", "ppid", "name", "cpu_percent","rss_bytes","snapshot")
    search_fields = ("name",)
