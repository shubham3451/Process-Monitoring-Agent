from django.db import models

# Create your models here.

class Host(models.Model):
    hostname = models.CharField(max_length=255, unique=True)
    os = models.CharField(max_length=255, blank=True, null=True)
    processor = models.CharField(max_length=255, blank=True, null=True)
    
    physical_cores = models.PositiveIntegerField(blank=True, null=True)
    logical_cores = models.PositiveIntegerField(blank=True, null=True)
    
    ram_total_gb = models.FloatField(blank=True, null=True)
    ram_used_gb = models.FloatField(blank=True, null=True)
    ram_available_gb = models.FloatField(blank=True, null=True)
    
    disk_total_gb = models.FloatField(blank=True, null=True)
    disk_used_gb = models.FloatField(blank=True, null=True)
    disk_free_gb = models.FloatField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hostname


    def __str__(self):
        return self.hostname

class Snapshot(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name="snapshots")
    snapshot_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-snapshot_time"]

    def __str__(self):
        return f"{self.host.hostname} @ {self.snapshot_time.isoformat()}"

class Process(models.Model):
    snapshot = models.ForeignKey(Snapshot, on_delete=models.CASCADE, related_name="processes")
    pid = models.IntegerField(db_index=True)
    ppid = models.IntegerField(db_index=True)
    name = models.CharField(max_length=512)
    cpu_percent = models.FloatField()
    rss_bytes = models.BigIntegerField()
