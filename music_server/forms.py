from django.forms import forms, ModelForm, CharField

from music_server.models import Item, YouTubeQueue

class UploadForm(ModelForm):
    class Meta:
        model = Item
        fields = ('file',)

class YouTubeForm(ModelForm):
    class Meta:
        model = YouTubeQueue
        fields = ('uri',)

class SpotifyForm(ModelForm):
    class Meta:
        model = Item
        fields = ('spotify',)
