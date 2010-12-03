import os
import sys
import time
import signal
import datetime
import subprocess

from optparse import make_option
from django.conf import settings
from django.core.management.base import BaseCommand

from music_server.models import Item

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--verbosity', action='store', dest='verbosity', default='1',
            type='choice', choices=['0', '1', '2'],
            help='Verbosity level; 0=minimal output, 1=normal output, 2=all output'),
    )
    help = 'Play queued media'
    args = ''

    def handle(self, *app_labels, **options):
        verbosity = int(options['verbosity'])

        if verbosity > 1: print "Re-queuing all 'downloading' items"
        for item in Item.objects.filter(state='p'):
            item.state = 'x'
            item.save()

        if verbosity > 1: print "Entering mainloop"
        while True:
            try:
                item = Item.unplayed.all()[0]

                if verbosity > 1: print "Marking %s as playing" % item
                item.state = 'p'
                item.save()

                if item.file:
                    cmd = ['mplayer', '-fs', '-af', 'volnorm', '-vo', 'sdl', item.file.path]
                else:
                    cmd = ['./spotify.sh',item.spotify]

                if verbosity > 1: print "Executing '%s'" % ' '.join(cmd)

                start = datetime.datetime.now()
                p = subprocess.Popen(cmd)
                while p.poll() is None:
                    if datetime.datetime.now() > start + datetime.timedelta(minutes=20):
                        if verbosity > 1: print "Killing music player after timeout"
                        os.kill(p.pid, signal.SIGHUP)
                    time.sleep(1)

                item.state = 'x'
                item.save()

            except IndexError:
                if verbosity > 1: print "No items, sleeping for a while"
                time.sleep(5)
