import sys
import glob
import time
import shutil
import os.path
import tempfile
import subprocess

from optparse import make_option
    
from django.conf import settings
from django.core.files.base import File
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage

from music_server.models import Item, YouTubeQueue, upload_filename

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--verbosity', action='store', dest='verbosity', default='1',
            type='choice', choices=['0', '1', '2'],
            help='Verbosity level; 0=minimal output, 1=normal output, 2=all output'),
        #make_option('--daemonise', action='store_true', dest='daemonise', default=False,
        #    help='Daemonise'),
    )
    help = 'Download YouTube videos that have been queued'
    args = ''

    def handle(self, *app_labels, **options):
        verbosity = int(options['verbosity'])

        if verbosity > 1: print "Re-queuing all 'downloading' items"
        for item in YouTubeQueue.objects.filter(state='d'):
            item.state = 'q'
            item.save()

        if verbosity > 1: print "Removing all failed items"
        YouTubeQueue.objects.filter(state='f').delete()

        while True:
            time.sleep(2)

            if verbosity > 1: print "Going to try and dequeue item"
            try:
                item = YouTubeQueue.objects.filter(state='q')[0]
            except IndexError:
                continue

            if verbosity > 1: print "Updating state to downloading"
            item.state = 'd'
            item.save()

            tempdir = tempfile.mkdtemp('music-server-youtube')
            try:
                cmd = ['youtube-dl']
                if verbosity < 2:
                    cmd.append('--quiet')
                cmd.extend(['--title', item.uri])

                if verbosity > 1: print "Running '%s'" % " ".join(cmd)
                retcode = subprocess.call(cmd, cwd=tempdir)

                if verbosity > 1: print "youtube-dl returned with a status of %d" % retcode

                if retcode != 0:
                    item.state = 'f'
                    item.save()
                    continue

                filename = glob.glob(os.path.join(tempdir, '*'))[0]

                location = upload_filename(item, 'youtube-%s' % filename.split('/')[-1])
                if verbosity > 1: print "Saving file using Django storage engine to %s" % location

                storage_name = default_storage.save(location, File(file(filename)))

                if verbosity > 1: print "Creating new Item object"
                Item.objects.create(user=item.user, ip=item.ip, file=storage_name)

                if verbosity > 1: print "Deleting queue object"
                item.delete()
            finally:
                try:
                    if verbosity > 1: print "Going to delete temporary file"
                    shutil.rmtree(tempdir)
                except OSError, e:
                    if e.errno != 2: # "No such file or directory"
                        raise
