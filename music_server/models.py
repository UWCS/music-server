import re
import datetime

from django.db import models
from django.db import connection
from django.conf import settings
from django.contrib.auth.models import User

from music_server.managers import UnplayedItemManager

FILENAME_PAT = re.compile(r'[^ -.a-zA-Z0-9_]')

def upload_filename(instance, filename):
    return '%s' % FILENAME_PAT.sub('_', filename)

class Item(models.Model):
    CHOICES = (
        ('q', 'Queued'),
        ('p', 'Playing'),
        ('x', 'Played'),
    )

    user = models.ForeignKey(User)
    bucket = models.IntegerField()
    pos = models.IntegerField()

    file = models.FileField(upload_to=upload_filename, blank=True)
    spotify = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    ip = models.IPAddressField()
    state = models.CharField(max_length=1, choices=CHOICES, default='q')
    added = models.DateTimeField(auto_now_add=True, null=True)

    objects = models.Manager()
    unplayed = UnplayedItemManager()

    class Meta:
        ordering = ('bucket', 'pos')
        unique_together = ('bucket', 'pos')

    def __unicode__(self):
        return '%(file)s (state: %(state)s) queued by %(user)s (bucket %(bucket)d, position %(pos)d)' % {
            'file': self.file if self.file else self.spotify,
            'state': self.state,
            'user': self.user,
            'bucket': self.bucket,
            'pos': self.pos,
        }

    def is_new(self):
        return datetime.datetime.now() < self.added + datetime.timedelta(seconds=2)

    def save(self, *args, **kwargs):
        if self.id:
            super(Item, self).save()
        else:
            try:
                self.lock_table()

                try:
                    self.bucket = Item.objects.exclude(state='x').order_by('bucket').values_list('bucket', flat=True)[0]
                    while True:
                        if not Item.objects.filter(user=self.user, bucket=self.bucket).count():
                            break
                        self.bucket += 1

                except IndexError:
                    try:
                        self.bucket = Item.objects.latest('bucket').bucket+1
                    except Item.DoesNotExist:
                        self.bucket = 1

                try:
                    self.pos = Item.objects.filter(bucket=self.bucket).order_by('-pos').values_list('pos', flat=True)[0] + 1
                except IndexError:
                    self.pos = 1

                super(Item, self).save()

            finally:
                self.unlock_table()

    def str_filename(self):
        try:
            # Remove username
            return self.file.name.split('/', 1)[1]
        except IndexError:
            return self.file.name
    
    def get_title(self):
        if self.title:
            return self.title
        elif self.spotify:
            return self.spotify
        else:
            return self.str_filename()

    def move_up(self):
        try:
            try:
                self.lock_table()
                other = Item.objects.filter(bucket__lt=self.bucket, user=self.user, state='q').order_by('-bucket')[0]
                self._swap(self, other)
                return other
            except IndexError:
                # Don't allow item to arbitrarily move up a bucket
                pass
        finally:
            self.unlock_table()

    def move_down(self):
        try:
            try:
                self.lock_table()
                other = Item.objects.filter(bucket__gt=self.bucket, user=self.user, state='q').order_by('bucket')[0]
                self._swap(self, other)
                return other
            except IndexError:
                try:
                    max_bucket = Item.objects.all().order_by('-bucket').values_list('bucket', flat=True)[0]
                    self.bucket = min(self.bucket + 1, max_bucket)
                    self.save()
                except IndexError:
                    pass
        finally:
            self.unlock_table()

    def delete(self):
        try:
            self.lock_table()
            super(Item, self).delete()
        finally:
            self.unlock_table()

    def can_modify(self,user):
        return self.user == user or user.is_staff

    @classmethod
    def _swap(cls, item_1, item_2):
        item_1_bucket = item_1.bucket
        item_1_pos = item_1.pos
        item_2_bucket = item_2.bucket
        item_2_pos = item_2.pos

        item_1.bucket = -1
        item_1.pos = -1
        item_1.save()

        item_2.bucket = -2
        item_2.pos = -2
        item_2.save()

        item_1.bucket = item_2_bucket
        item_1.pos = item_2_pos
        item_1.save()

        item_2.bucket = item_1_bucket
        item_2.pos = item_1_pos
        item_2.save()

    @classmethod
    def lock_table(cls):
        return
        if not settings.DATABASE_ENGINE.startswith('sqlite'):
            cursor = connection.cursor()
            cursor.execute('LOCK TABLES %s WRITE' % cls._meta.db_table)

    @classmethod
    def unlock_table(cls):
        return
        if not settings.DATABASE_ENGINE.startswith('sqlite'):
            cursor = connection.cursor()
            cursor.execute('UNLOCK TABLES')

class Blackball(models.Model):
    user = models.ForeignKey(User)
    item = models.ForeignKey(Item)

class YouTubeQueue(models.Model):
    CHOICES = (
        ('q', 'Queued'),
        ('d', 'Downloading'),
        ('f', 'Download failed'),
    )

    user = models.ForeignKey(User)
    uri = models.URLField(verify_exists=False)
    ip = models.IPAddressField()

    added = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=1, choices=CHOICES, default='q')

    class Meta:
        ordering = ('added',)

    def __unicode__(self):
        return 'Queued download of %s by %s (%s)' % (self.uri, self.user, self.str_state())

    def str_state(self):
        return dict(self.CHOICES)[self.state]
