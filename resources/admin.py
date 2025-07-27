from django.contrib import admin
from .models import EC2Instance

@admin.register(EC2Instance)
class EC2InstanceAdmin(admin.ModelAdmin):
    list_display = ('name', 'aws_instance_id', 'status', 'instance_type', 'region', 'ip_address', 'creating_user', 'created_at')
    list_filter = ('status', 'instance_type', 'region', 'created_at')
    search_fields = ('name', 'aws_instance_id', 'ip_address', 'creating_user__email')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'creating_user', 'instance_type', 'region')
        }),
        ('AWS Details', {
            'fields': ('aws_instance_id', 'status', 'ip_address')
        }),
        ('Connection', {
            'fields': ('port', 'username', 'password', 'ssh_key'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('aws_instance_id', 'created_at', 'updated_at')
    
    actions = ['start_instances', 'stop_instances', 'refresh_status']
    
    def start_instances(self, request, queryset):
        for instance in queryset:
            instance.start_instance()
        self.message_user(request, f"Started {queryset.count()} instances")
    start_instances.short_description = "Start selected instances"
    
    def stop_instances(self, request, queryset):
        for instance in queryset:
            instance.stop_instance()
        self.message_user(request, f"Stopped {queryset.count()} instances")
    stop_instances.short_description = "Stop selected instances"
    
    def refresh_status(self, request, queryset):
        for instance in queryset:
            instance.get_instance_status()
            instance.get_instance_ip_address()
        self.message_user(request, f"Refreshed status for {queryset.count()} instances")
    refresh_status.short_description = "Refresh instance status and IP"
