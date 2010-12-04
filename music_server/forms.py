from django.forms import forms, ModelForm, CharField

from music_server.models import Item, YouTubeQueue

class UploadForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UploadForm, self).__init__(*args, **kwargs)

    def clean(self):
        if (Item.unplayed.filter(user=self.request.user).count() > 4):
            raise forms.ValidationError("You can only have up to 5 songs enqueued at a time")
        return self.cleaned_data

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

class ResubmitForm(ModelForm):
    class Meta:
        model = Item
        fields = ('id',)
