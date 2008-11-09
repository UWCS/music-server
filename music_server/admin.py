from django.contrib import admin

from music_server.models import Item, YouTubeQueue

class ItemAdmin(admin.ModelAdmin): pass
admin.site.register(Item, ItemAdmin)

class YouTubeQueueAdmin(admin.ModelAdmin): pass
admin.site.register(YouTubeQueue, YouTubeQueueAdmin)
