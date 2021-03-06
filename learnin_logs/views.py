from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import Topic, Entry
from .forms import TopicForm, EntryForm

# Create your views here.

def index(request):
    """The homepage for learnin_logs"""
    return render(request, 'learnin_logs/index.html')


def topic_owner(request, topic):
    # check if the current user is the owner of the topic
    if topic.owner != request.user:
        raise Http404


@login_required
def topics(request):
    """Shows all topics"""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learnin_logs/topics.html', context)


@login_required
def topic(request, topic_id):
    """Shows a single topic and all its entries"""
    topic = get_object_or_404(Topic, id=topic_id)
    # make sure the topic belongs to the current user.
    topic_owner(request,topic)

    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return  render(request, 'learnin_logs/topic.html', context)


@login_required
def new_topic(request):
    """Add a new topic"""
    if request.method != 'POST':
        #No data submitted; create a blank form
        form = TopicForm()
    else:
        # POST data submitted; process data
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learnin_logs:topics')

    # Display a blank or invalid form
    context = {'form': form}
    return render(request, 'learnin_logs/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    """Adds a new entry for a particular topic"""
    topic = Topic.objects.filter(owner=request.user).get(id=topic_id)
    topic_owner(request, topic)

    if request.method != 'POST':
        #No data submitted; create a blank form.
        form = EntryForm()
    else:
        # POST data submitted; process data
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.owner = request.user
            new_entry.save()
            return  redirect('learnin_logs:topic', topic_id=topic_id)

    # Display a blank or invalid form
    context = {'topic': topic, 'form': form}
    return render(request, 'learnin_logs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    topic_owner(request, topic)

    if request.method != 'POST':
        # initial request; pre-fill form wth current entry
        form = EntryForm(instance=entry)
    else:
        # POST data submitted; process data
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return  redirect('learnin_logs:topic', topic_id=topic.id)

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learnin_logs/edit_entry.html', context)


@login_required
def edit_topic(request, topic_id):
    """Edit existing topic"""
    topic = Topic.objects.filter(owner=request.user).get(id=topic_id)

    if request.method != 'POST':
        # initial request; pre-fill form with current topic
        form = TopicForm(instance=topic)
    else:
        # POST data submitted; process data
        form = TopicForm(instance=topic, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learnin_logs:topic', topic_id=topic.id)

    context = {'topic': topic, 'form': form}
    return render(request, 'learnin_logs/edit_topic.html', context)


@login_required
def delete_topic(request, topic_id):
    """Delete a topic"""
    topic = Topic.objects.filter(owner=request.user).get(id=topic_id)
    topic.delete()
    return redirect('learnin_logs:topics')


@login_required
def delete_entry(request, entry_id):
    """Delete a topic"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    topic_owner(request, topic)
    entry.delete()
    return redirect('learnin_logs:topic', topic_id=topic.id)
