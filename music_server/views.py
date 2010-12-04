from itertools import count, izip

from django.db import connection
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.forms import forms

from music_server.forms import UploadForm, YouTubeForm, SpotifyForm
from music_server.models import Item, YouTubeQueue

from tagging import get_name,spotify_name

def index(request):
    if request.method == 'POST':
        if not request.user.is_authenticated():
            return HttpResponseRedirect('%s?next=%s' % (reverse('login', request.path)))

        form = UploadForm(request.POST, request.FILES, request=request)
        return save_and_commit(form,'index',request,'file')
    else:
        form = UploadForm()

    return render_to_response('index.html', {
        'queue': izip(count(1), Item.unplayed.all()),
        'upload_form': form,
        'youtube_form': YouTubeForm(),
        'spotify_form': SpotifyForm(),
    }, RequestContext(request))

def history(request,user_id):
    return render_to_response('history.html', {
        'history_user':get_object_or_404(User,id=user_id),
        'history': get_list_or_404(Item,user__id=user_id),
    }, RequestContext(request))


def spotify(request):
    '''
        Uses index for rendering
    '''
    if request.method == 'POST':
        if not request.user.is_authenticated():
            return HttpResponseRedirect('%s?next=%s' % (reverse('login', request.path)))

        form = SpotifyForm(request.POST)
        return save_and_commit(form,'index',request,'spotify')

def save_and_commit(form,redir,request,field):
    if form.is_valid() and form.cleaned_data[field]:
        q = form.save(commit=False)
        q.user = request.user
        q.ip = request.META.get('REMOTE_ADDR')
        q.save()
        if redir != 'youtube':
            if q.file:
                q.title = get_name(q.file.path)[:255]
            else:
                q.title = spotify_name(q.spotify)[:255]

        q.save()
        return HttpResponseRedirect(reverse(redir))
    else:
        return HttpResponseRedirect(reverse('index'))

def xhr_queue(request):
    return render_to_response('queue.html', {
        'queue': izip(count(1), Item.unplayed.all()),
    }, RequestContext(request))

def youtube(request):
    if request.method == 'POST':
        if not request.user.is_authenticated():
            return HttpResponseRedirect('%s?next=%s' % (reverse('login', request.path)))

        form = YouTubeForm(request.POST)
        return save_and_commit(form,'youtube',request,'uri')
    else:
        form = YouTubeForm()

    return render_to_response('youtube.html', {
        'youtube_form': form,
        'queue': YouTubeQueue.objects.exclude(state='f'),
        'failed': YouTubeQueue.objects.filter(state='f')[:5],
    }, RequestContext(request))

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            d = form.cleaned_data
            user = authenticate(username=d['username'], password=d['password1'])
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = UserCreationForm()

    return render_to_response('registration/register.html', {
        'form': form,
    }, RequestContext(request))

@login_required
def delete(request, item_id):
    if request.user.is_staff:
        get_object_or_404(Item, id=item_id, state='q').delete()
    else:
        get_object_or_404(Item, id=item_id, user=request.user, state='q').delete()
    return HttpResponseRedirect(reverse('index'))

@login_required
def move(request, direction, item_id):
    item = get_object_or_404(Item, id=item_id, user=request.user, state='q')
    if direction == 'up':
        val = item.move_up()
    else:
        val = item.move_down()

    if request.is_ajax():
        if val is None:
            return HttpResponse(0)
        else:
            return HttpResponse(val.id)

    return HttpResponseRedirect(reverse('index'))
