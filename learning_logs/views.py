from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import Topic, Entry
from .forms import TopicForm, EntryForm

def index(request):
    """Домашняя страница приложения Learning Log"""
    return render(request, 'learning_logs/index.html')

def topics(request):
    """
    Показать все темы текущего пользователя и общедоступные темы,
    принадлежащие другим пользователям
    """
    # Если пользователь вошел в систему, мы получаем все его темы и все
    # общедоступные темы от других пользователей
    if request.user.is_authenticated:
        topics = Topic.objects.filter(owner=request.user).order_by('date_added')
        # Получить все общедоступные темы, не принадлежащие текущемы пользователю
        public_topics = (Topic.objects
            .filter(public=True)
            .exclude(owner=request.user)
            .order_by('date_added'))
    else:
        # Пользователь не аутентифицирован; вернуть все публичные темы
        topics = None
        public_topics = Topic.objects.filter(public=True).order_by('date_added')
    
    context = {'topics': topics, 'public_topics': public_topics}
    return render(request, 'learning_logs/topics.html', context)
  
def topic(request, topic_id):
    """Выводит одну тему и все ее записи"""
    topic = Topic.objects.get(id=topic_id)
    
    # Мы хотим показываеть ссылки new_entry и edit_entry только в том случае,
    # если текущий пользователь владеет темой
    is_owner = False
    if request.user == topic.owner:
        is_owner = True
    
    # Если тема принадлежит кому-то другому и не является общедоступной, то 
    # показать страницу с ошибкой 404
    if (topic.owner != request.user) and (not topic.public):
        raise Http404
        
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries, 'is_owner': is_owner}
    return render(request, 'learning_logs/topic.html', context)
        
@login_required
def new_topic(request):
    """Добавляет новую тему"""
    if request.method != 'POST':
        # Данные не отправлялись; создается пустая форма
        form = TopicForm()
    else:
        # Отправлены данные POST; обработать данные
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')
    
    # Показать пустую или недействительную форму
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)
    
@login_required    
def new_entry(request, topic_id):
    """Добавляет новую запись по конкретной теме"""
    topic = get_object_or_404(Topic, id=topic_id)
    check_topic_owner(topic, request.user)
    
    if request.method != 'POST':
        # Данные не отправлялись; создается пустая форма
        form = EntryForm()
    else:
        # Отправлены данные POST; обработать данные
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)
    
    # Показать пустую или недействительную форму
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)
    
@login_required    
def edit_entry(request, entry_id):
    """Редактирует существующую запись"""
    entry = get_object_or_404(Entry, id=entry_id)
    topic = entry.topic
    check_topic_owner(topic, request.user)
    if request.method != 'POST':
        # Исходный запрос; форма заполняется данными текущей записи
        form = EntryForm(instance=entry)
    else:
        # Отправка данных POST; обработать данные
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid:
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)
            
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)
    
def check_topic_owner(topic, user):
    """
    Проверяет, что пользователь, связанный с темой,
    является текущим пользователем
    """
    if topic.owner != user:
        raise Http404
    
