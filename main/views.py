from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import update_last_login
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from django.http import HttpResponse
from django.http import JsonResponse
import json
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models import Q
from django.template import loader
#from django.conf.urls import url
from django.contrib.contenttypes.fields import GenericForeignKey
from django.shortcuts import render, redirect
from .forms import sign
import pprint
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.auth.forms import PasswordResetForm
from main.tokens import account_activation_token
from django.db.models import Q
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import View
from django.contrib.auth import get_user_model
from operator import and_, or_
import operator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProfileSerializer
from .serializers import PostSerializer
from .serializers import JobSerializer
from .serializers import MessageSerializer
from .serializers import NotificationSerializer
from .serializers import GroupSerializer
from .serializers import TopicSerializer
from .serializers import LoginSerializer
from .serializers import RegisterSerializer
from rest_framework import permissions
from functools import reduce
from .models import Topic, User_Groups
from .models import Post, Comment, Repost, Job, Liked_Post, Profile, Message, Notification, Flagged_Post, User_Groups
from .forms import CommentForm
from .forms import PostForm
from .forms import ProfileForm, ImageForm, MessageForm, DMPostForm, GroupForm
from django.core.files.storage import FileSystemStorage
from django.views.generic import TemplateView, ListView
from django.utils.decorators import method_decorator
import json
from geopy.geocoders import Nominatim
import requests
import urllib.parse


def index(request):
    User = get_user_model()
    users = User.objects.all()
    all_posts = Post.objects.all().order_by('Created').reverse()
    all_reposts = Repost.objects.all().order_by('Created').reverse()
    all_liked = Liked_Post.objects.all()
    com = Comment.objects.filter().count
    #following = Follow.objects.following(request.user)
    #default_pic = default_Profile_pic.objects.all()
    post_list = zip(all_posts, all_reposts)
    form = PostForm(request.POST or None)
    dmForm = MessageForm(request.POST or None)
    group_form = GroupForm(request.POST or None)
    Author = request.user
    
    if request.method == 'POST':
        job = form.save(commit=False)
        
        job.save()
        form = PostForm(request.POST or None, instance=job)
        
        form.save()
        return HttpResponse('<script>history.back();</script>')
            
    else:
        form = PostForm()    
        dmForm = MessageForm()
        group_form = GroupForm()
        
    context = {
        'User': users,
        'all_posts': all_posts,
        #'following': following,
        'form': form,
        'Author': Author,
        'all_reposts': all_reposts,
        'all_liked': all_liked,
        'post_list': post_list,
        'dmForm': dmForm,
        'group_form': group_form,
    }
    template = loader.get_template('main/index.html')
    
    return HttpResponse(template.render(context, request))


def inbox(request, username):
    User = get_user_model()
    user = User.objects.get(username=username)
    DMs = Message.objects.filter(receiver=request.user)
    default_pic = default_Profile_pic.objects.all()
    form = MessageForm(request.POST or None)
    if request.method == 'POST':
        if 'msg' in request.POST:
            if form.is_valid():
                message = form.save(commit=False)
                message.sender = request.user
                message.save(request.POST['msg_content'])
                #Message.objects.create(sender=request.user, receiver=message.receiver)
                #return redirect('Purefun/inbox.html')
        else:
            form = MessageForm()
    template = loader.get_template('main/inbox.html')
    context = {
        'DMs': DMs,
        'user': user,
        'form': form,
    }
    return HttpResponse(template.render(context, request)) 

@csrf_exempt
def signout(request):
    logout(request)
    return render(request, 'main/about.html') 

def about(request):
    
    return render(request, 'main/about.html')    


#def login(request):
    
    #return render(request, 'main/login.html')    

    
def signup(request):
    if request.method == 'POST':
        form = sign(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            #user.profile.birth_date = form.cleaned_data.get('birth_date')
            user.is_staff = False
            user.is_superuser = False
            user.is_admin = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your Purefun Account'
            message = render_to_string('main/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            login(request, user)
            user.email_user(subject, message)
            return render(request, 'main/account_activation_sent.html')
    else:
        form = sign()
    return render(request, 'main/signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = user.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.Profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'main/account_activation_invalid.html')

        
def account_activation_sent(request):
    return render(request, 'activate')


def account_activation_email(request):
    return render(request, 'activate')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = user.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.Profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'main/account_activation_invalid.html')    


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return render(request, 'main/login.html', {'albums': albums})
            else:
                return render(request, 'main/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'main/login.html', {'error_message': 'Invalid login'})
    return render(request, 'main/login.html')


def user_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    template = loader.get_template('main/user_Profile.html')
    context = {
        'User': user,
    }
    return HttpResponse(template.render(context, request))


def get_user_profile(request, username):
    
    user = User.objects.get(username=username)
    user_posts = Post.objects.filter(Author=user).order_by('Created').reverse()
    all_reposts = Repost.objects.filter(Reposter=user).order_by('Created').reverse()
    #following = Follow.objects.following(user)
    #followers = Follow.objects.followers(user)
    DMs = Message.objects.filter(receiver=request.user)
    default_pic = default_Profile_pic.objects.all()
    template = loader.get_template('main/user_Profile.html')
    context = {
        'user': user,
        "user_posts":user_posts,
        'all_reposts': all_reposts,
        'DMs': DMs,
        'default pic': default_pic,
    }
    followee = user
    follower = request.user
    if request.method == "POST":   
        if 'follow' in request.POST:
            #Follow.objects.add_follower(follower, followee)
            #Follow_obj.objects.create(user=user, user_follower=request.user)
            if user.Profile.isPrivate == True:
                sendFollowRequest(request, user)
                
            else:
                request.user.Profile.User_Following.add(user)
                request.user.Profile.Following_Count += 1
                request.user.Profile.save()
                user.Profile.User_Followers.add(request.user)
                user.Profile.Notifications += 1
                user.Profile.Follower_Count += 1
                user.Profile.save()
                Notification.objects.create(sender=request.user, receiver=user, is_follow_notification=True, msg="")
                
            
            return HttpResponse('<script>history.back();</script>')
            

        elif 'unfollow' in request.POST:
           # Follow.objects.remove_follower(follower, followee)
            request.user.Profile.User_Following.remove(user)
            request.user.Profile.Following_Count -= 1
            request.user.Profile.save()
            user.Profile.User_Followers.remove(request.user)
            user.Profile.Follower_Count -= 1
            user.Profile.save()
            return HttpResponse('<script>history.back();</script>')
            
        elif 'block' in request.POST:
            request.user.Profile.User_Following.remove(user)
            user.Profile.User_Followers.remove(request.user)
            user.Profile.save()
            request.user.Profile.Blocked_Users.add(user)
            request.user.Profile.save()
            return HttpResponse('<script>history.back();</script>')
            
        elif 'unblock' in request.POST:
            request.user.Profile.Blocked_Users.remove(user)
            return HttpResponse('<script>history.back();</script>')
            
        elif 'mute' in request.POST:
            request.user.Profile.Muted_Users.add(user)
            request.user.Profile.save()
            return HttpResponse('<script>history.back();</script>')
            
        elif 'unmute' in request.POST:
            request.user.Profile.Muted_Users.remove(user)
            request.user.Profile.save()
            return HttpResponse('<script>history.back();</script>')  
 
    editable = False

    return HttpResponse(template.render(context, request))


def go_private(request, username):
    
    user = User.objects.get(username=username)
    user.Profile.isPrivate = True
    user.Profile.save()
    return HttpResponse('<script>history.back();</script>')
        
    template = loader.get_template('main/index.html')
    context = {
        'user': user,
    }
    return HttpResponse('<script>history.back();</script>')
    
    return HttpResponse(template.render(context, request))
    

def go_public(request, username):
    
    user = User.objects.get(username=username)
    user.Profile.isPrivate = False
    user.Profile.save()
    return HttpResponse('<script>history.back();</script>')
        
    template = loader.get_template('main/index.html')
    context = {
        'user': user,
    }
    return HttpResponse('<script>history.back();</script>')
    
    return HttpResponse(template.render(context, request))     


def followers(request, username, template_name="main/user_Profile.html"):
   
    user = get_object_or_404(user_model, username=username)
    followers = Follow.objects.followers(user)
    return render(
        request,
        template_name,
        {
            get_friendship_context_object_name(): user,
            "friendship_context_object_name": get_friendship_context_object_name(),
            "followers": followers,
        },
    )


def following(request, username, template_name="main/user_Profile.html"):
   
    user = get_object_or_404(user_model, username=username)
    following = Follow.objects.following(user)
    return render(
        request,
        template_name,
        {
            get_friendship_context_object_name(): user,
            "friendship_context_object_name": get_friendship_context_object_name(),
            "following": following,
        },
    )


def report(request, username):
    
    user = User.objects.get(username=username)
    template = loader.get_template('main/report.html')
    context = {
        'user': user,
    }
    if request.method == 'POST':
        form = report(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db() 
            user.save()
            current_site = get_current_site(request)
            return render(request, 'main/edit_profile.html')
    else:
        form = report()  
    editable = False
    if request.user.is_authenticated() and request.user == user:
        editable = True
    return HttpResponse(template.render(context, request))    


def post_detail(request, post_id):
    
    post = get_object_or_404(Post, pk=post_id)
    com = Comment.objects.filter(post_id=post_id).count
    all_comments = Comment.objects.filter(post_id=post_id).order_by('created').reverse()
    user = User.objects.get(username=request.user)
    
    try:
        comments = post.comments
    except:
        comments = None
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if 'comment' in request.POST:
            if form.is_valid():
                comment = form.save(commit=False)
                comment.Author = request.user
                comment.post = post
                post.CommentCount += 1
                post.Comment.add(user)
                post.save()
                comment.save(request.POST['body'])
                user.Profile.Notifications += 1
                Notification.objects.create(post=post, sender=request.user, receiver=user, is_comment_notification=True, msg="")
                user.Profile.save()
                return redirect('post_detail', post_id=post_id)

    else:
        comment_form = CommentForm()                   
    return render(request,
                  'main/post_detail.html',
                  {'post': post,
                   'comments': comments,
                   'com': com,
                   'all_comments': all_comments,
                   'comment_form': comment_form,
                   })
                   

def repost_detail(request, Repost_id):
    
    repost = get_object_or_404(Repost, pk=Repost_id)
    all_comments = Comment.objects.filter(post_id=repost.id).order_by('created').reverse()
    
    try:
        comments = repost.comments
    except:
        comments = None
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if 'comment' in request.POST:
            if form.is_valid():
                repostcomment = form.save(commit=False)
                repostcomment.Author = request.user
                repostcomment.repost = repost
                repostcomment.save(request.POST['body'])
                return redirect('repost_detail', Repost_id=Repost_id)

    else:
        comment_form = CommentForm()                   
    return render(request,
                  'main/repost_detail.html',
                  {'repost': repost,
                   'comments': comments,
                   'all_comments': all_comments,
                   'comment_form': comment_form,
                   })

        
def DMPost(request, post_id, username):
    post = get_object_or_404(Post, pk=post_id)
    user = User.objects.get(username=request.user)
    form = MessageForm(request.POST or None)
    if request.method == 'POST':
        if 'dm' in request.POST:
            if form.is_valid():
                message = form.save(commit=False)
                message.sender = request.user
                message.receiver = (request.POST['receiver'])
                message.post = post
                message.save(request.POST['msg_content'])
                Message.objects.create(sender=request.user, receiver=message.receiver)
                return redirect('main/inbox.html')
        
    else:
        form = MessageForm()
        
    template = loader.get_template('main/inbox.html')
    context = {
        'post': post,
        'like': like,
        'form': form,
        #'liked': liked,
    }
    #return redirect('index')
    
    return HttpResponse(template.render(context, request))    


def flag(request, post_id):
    
    post = get_object_or_404(Post, pk=post_id)
    Flagged_Post.objects.create(post=post)
    post.Flags.add(request.user)
    post.save()
    return HttpResponse('<script>history.back();</script>')
        
    template = loader.get_template('main/index.html')
    context = {
        'post': post,
    }
    return redirect('index')
    
    return HttpResponse(template.render(context, request)) 

    
def unrepost(request, post_id):
    
    post = get_object_or_404(Post, pk=post_id)
    user = User.objects.get(username=request.user)
    post.Reposts.remove(user)
    post.ReshareCount -= 1
    #post.objects.filter(id=id).delete()
    #post.IsRepost = False
    post.save()
    return HttpResponse('<script>history.back();</script>')
        
    template = loader.get_template('main/index.html')
    context = {
        'post': post,
        'like': like,
        #'liked': liked,
    }
    return redirect('index')
    
    return HttpResponse(template.render(context, request))    


def like(request, post_id, username):
    post = get_object_or_404(Post, pk=post_id)
    user = User.objects.get(username=username)
    post.Likes.add(request.user)
    post.LikeCount += 1
    user.Profile.Notifications += 1
    Notification.objects.create(post=post, sender=request.user, receiver=user, is_like_notification=True, msg="")
    #Flagged_Post.objects.create(post=post)
    user.Profile.save()
    post.save()
    return redirect('index')
        
    template = loader.get_template('main/index.html')
    context = {
        'post': post,
        'like': like,
        #'liked': liked,
    }
    return HttpResponse(template.render(context, request))
    
    
def unlike(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = User.objects.get(username=request.user)
    post.Likes.remove(user)
    post.LikeCount -= 1
    post.save()
    return HttpResponse('<script>history.back();</script>')
        
    template = loader.get_template('main/index.html')
    context = {
        'post': post,
        'like': like,
        #'liked': liked,
    }
    return HttpResponse(template.render(context, request))  
 
    
def comment(request, post_id):
    User = get_user_model()
    users = User.objects.all()
    com = Comment.objects.filter().count
    following = Follow.objects.following(request.user)
    default_pic = default_Profile_pic.objects.all()
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if 'post' in request.POST:
            if form.is_valid():
                Content = form.save(commit=False)
                Content.Author = request.user
                Content.save(request.POST['Content'])
                post = get_object_or_404(Post, pk=post_id)
                post.Comment.add(user)
                post.CommentCount += 1
                post.save()
                return redirect('index')
        
    template = loader.get_template('main/index.html')
    context = {
        'post': post,
        'like': like,
    }
    return redirect('index')
    
    return HttpResponse(template.render(context, request))

    
def message(request, post_id):
    User = get_user_model()
    users = User.objects.all()
    post = get_object_or_404(Post, pk=post_id)
    com = Comment.objects.filter().count
    default_pic = default_Profile_pic.objects.all()
    form = MessageForm(request.POST or None)
    if request.method == 'POST':
        if 'msg' in request.POST:
            if form.is_valid():
                msg_content = form.save(commit=False)
                msg_content.sender = request.user
                msg_content.post = post
                msg_content.save(request.POST['msg_content'])
                return redirect('index')
        
    template = loader.get_template('main/index.html')
    context = {
        'post': post,
        'like': like,
        #'liked': liked,
    }
    return redirect('inbox', request.user.username)
    
    return HttpResponse(template.render(context, request))

    
def msg(request, post_id):
    User = get_user_model()
    users = User.objects.all()
    user = request.user
    post = get_object_or_404(Post, pk=post_id)
    com = Comment.objects.filter().count
    default_pic = default_Profile_pic.objects.all()
    dmForm = MessageForm(request.POST or None)
    #user.Profile.MessagesCount += 1
    if request.method == 'POST':
        if 'dm' in request.POST:
            if dmForm.is_valid():
                post = get_object_or_404(Post, pk=post_id)
                msg_content = dmForm.save(commit=False)
                msg_content.post = post
                msg_content.sender = request.user
                user.Profile.MessagesCount += 1
                user.save()
                msg_content.save(request.POST['msg_content'])
                return HttpResponse('<script>history.back();</script>')
    else:
        dmForm = MessageForm()
        
    template = loader.get_template('main/index.html')
    context = {
        'post': post,
        'like': like,
        #'liked': liked,
    }
    return redirect('inbox', request.user.username)
    
    return HttpResponse(template.render(context, request))
    

def group(request):
    #user = User.objects.get(request.user)
    users = User.objects.all()
    groups = User_Groups.objects.all()
    group_form = GroupForm(request.POST or None)
    if request.method == 'POST':
        if 'group' in request.POST:
            if group_form.is_valid():
                group = group_form.save(commit=False)
                group.save()
                group.user = request.user
                group.Label = request.POST['Label']
                group.Members.set()
                group.save()
                return HttpResponse('<script>history.back();</script>')
    else:
        group_form = GroupForm()
        
    template = loader.get_template('main/index.html')
    context = {
        'group_form': group_form,
    }
    return HttpResponse('<script>history.back();</script>')
    
    return HttpResponse(template.render(context, request))   


def edit_profile(request):
    
    form = ProfileForm(request.POST or None)
    template = loader.get_template('main/index.html')
    if request.method == 'POST':
        if form.is_valid():
            form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user.Profile)
            user = form.save()
            user.birth_date = form.cleaned_data.get('birth_date')
            user.is_staff = True
            user.is_superuser = True
            user.is_admin = True
            user.Profile_Picture = form.cleaned_data['Profile_pic']
            files = request.FILES.getlist('Profile_Picture')
            fs = FileSystemStorage()
            #if self.request.FILES:
                #for afile in self.request.FILES.getlist('Profile_Picture'):
                    #img = Profile.objects.create(Profile_picture=afile)
            user.save()
            return redirect('index')
    else:
        form = ProfileForm()                   
    return render(request,'main/edit_profile.html',{'form': form,})


def add_post(request):
    
    form = PostForm(request.POST or None)
    template = loader.get_template('main/index.html')
    if request.method == 'POST':
        if form.is_valid():
            form = PostForm(request.POST or None, request.FILES or None, instance=request.user.Profile)
            user = form.save()
            user.Image = form.cleaned_data['Image']
            files = request.FILES.getlist('Image')
            fs = FileSystemStorage()
            user.save()
            return redirect('index')
    else:
        form = ProfileForm()                   
    return render(request,'main/edit_profile.html',{'form': form,})


def SearchView(request):
  
  query = request.GET.get('q','')
   
  if query:
    post_queryset = (Q(Content__icontains=query))
    user_queryset = (Q(username__icontains=query))
    #queryset = (Q(text__icontains=query))|(Q(other__icontains=query))
    post_results = Post.objects.filter(post_queryset).distinct()
    user_results = User.objects.filter(user_queryset).distinct()
    #topic_results = Topic.objects.filter(queryset).distinct()
  else:
       post_results = []
  return render(request, 'main/search.html', {'post_results':post_results,
  'user_results':user_results,
  'query':query,
  })


def addNotification(request, username, post_id):
    user = User.objects.get(username=request.user)
    user.Profile.Notifications += 1
    user.save()
    return HttpResponse('<script>history.back();</script>')
        
    template = loader.get_template('main/index.html')
    context = {
        'post': post,
        'like': like,
        #'liked': liked,
    }
    return HttpResponse(template.render(context, request))

    
def viewNotifications(request):
    Notifications = Notification.objects.all()
    return HttpResponse('<script>history.back();</script>')
        
    template = loader.get_template('main/index.html')
    context = {
        'post': post,
        'Notifications': Notifications,
    }
    return HttpResponse(template.render(context, request))    
    
    
def removeNotifications(request):
    user = request.user
    all_Notifications = Notification.objects.all()
    user.Profile.Notifications = 0
    user.Profile.save()
    #user.save()
        
    template = loader.get_template('main/notifications.html')
    context = {
        'all_Notifications': all_Notifications,
    }
    return HttpResponse(template.render(context, request))

    
def topics(request, label):
    topic = Topic.objects.filter(Topic__Label__icontains=label)
    all_topics = Topic.objects.all() 
    template = loader.get_template('Purefun/topics.html')
    context = {
        'topic': topic,
        'all_topics': all_topics,
    }
    return HttpResponse(template.render(context, request))     
 

  
def get_client_ip(request):
    remote_address = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
    ip = remote_address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        proxies = x_forwarded_for.split(',')
        while (len(proxies) > 0 and proxies[0].startswith(PRIVATE_IPS_PREFIX)):
            proxies.pop(0)
            if len(proxies) > 0:
                ip = proxies[0]
                #print"IP Address",ip
        return ip

def queryset_iterator(qs, batchsize = 500, gc_collect = True):
    iterator = qs.values_list('pk', flat=True).order_by('pk').distinct().iterator()
    eof = False
    while not eof:
        primary_key_buffer = []
        try:
            while len(primary_key_buffer) < batchsize:
                primary_key_buffer.append(iterator.next())
        except StopIteration:
            eof = True
        for obj in qs.filter(pk__in=primary_key_buffer).order_by('pk').iterator():
            yield obj
        if gc_collect:
            gc.collect()        


SESSION_KEY = '_auth_user_id'
BACKEND_SESSION_KEY = '_auth_user_backend'
HASH_SESSION_KEY = '_auth_user_hash'
REDIRECT_FIELD_NAME = 'next'
LANGUAGE_SESSION_KEY = '_language'
permission_classes = [permissions.AllowAny]
def loginn(request, user, backend=None):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request. Note that data set during
    the anonymous session is retained when the user logs in.
    """
    session_auth_hash = ''
    if user is None:
        user = request.user
    if hasattr(user, 'get_session_auth_hash'):
        session_auth_hash = user.get_session_auth_hash()

    if SESSION_KEY in request.session:
        if _get_user_session_key(request) != user.pk or (
                session_auth_hash and
                not constant_time_compare(request.session.get(HASH_SESSION_KEY, ''), session_auth_hash)):
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()

    try:
        backend = backend or user.backend
    except AttributeError:
        backends = _get_backends(return_tuples=True)
        if len(backends) == 1:
            _, backend = backends[0]
        else:
            raise ValueError(
                'You have multiple authentication backends configured and '
                'therefore must provide the `backend` argument or set the '
                '`backend` attribute on the user.'
            )

    request.session[SESSION_KEY] = user.pk
    request.session[BACKEND_SESSION_KEY] = backend
    request.session[HASH_SESSION_KEY] = session_auth_hash
    if hasattr(request, 'user'):
        request.user = user
    rotate_token(request)
    user_logged_in.send(sender=user.__class__, request=request, user=user)        


def removeNotifications(request):
    user = request.user
    all_Notifications = Notification.objects.all()
    user.profile.Notifications = 0
    user.profile.save()
    #user.save()
        
    template = loader.get_template('main/notifications.html')
    context = {
        'all_Notifications': all_Notifications,
    }
    return HttpResponse(template.render(context, request))
    

@csrf_exempt            
@method_decorator(csrf_exempt, name='assignJob')
def assignJob(request, job_id):
    permission_classes = [permissions.AllowAny]
    job = get_object_or_404(Job, pk=job_id)
    usr = request.user
    job.Assigned_Lugger = usr
    job.InProgress = True
    job.save()

    return render(request=request, template_name="main/login.html", context={"login_form":job})


def assign(request, job_id):
    permission_classes = [permissions.AllowAny]
    job = get_object_or_404(Job, pk=job_id)
    usr = request.user
    job.Assigned_Lugger = usr
    job.InProgress = True
    job.save()

    return render(request=request, template_name="main/login.html", context={"login_form":job})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("main:homepage")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="main/login.html", context={"login_form":form})


permission_classes = [permissions.AllowAny]            
@method_decorator(csrf_exempt, name='post')
class Login2ViewSet(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        #permission_classes = [permissions.IsAuthenticated]
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.validate(data=request.data)
        if serializer.is_valid():
            username = request.data.get('username')
            password = request.data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                #return redirect("main:homepage")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
        form = AuthenticationForm()
        return render(request=request)  
    
       
permission_classes = [permissions.AllowAny]            
@method_decorator(csrf_exempt, name='post')
class LoginViewSet(APIView):
    permission_classes = [permissions.AllowAny]
    @csrf_exempt
    def post(self, request):
        #permission_classes = [permissions.IsAuthenticated]
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.validate(data=request.data)
        username = request.data.get('username')
        password = request.data.get('password')	
        user = authenticate(username=username, password=password)
        pp = pprint.PrettyPrinter(indent=4)
        login(request, user)
        update_last_login(None, user)
        pp.pprint("logged in")
        pp.pprint(user.pk)
        pp.pprint(username)
        pp.pprint(password)
        token = account_activation_token.make_token(user)
        pp.pprint(token)
        user.is_active = True
        request.user = user
        pp.pprint(request.user)
        user_logged_in.send(sender=user.__class__, request=request, user=user) 
        return HttpResponseRedirect('/profiles/')

        
    def get(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.validate(data=request.data)
        username = request.data.get('username')
        password = request.data.get('password')	
        user = authenticate(username=username, password=password)
        pp = pprint.PrettyPrinter(indent=4)
        login(request)
        update_last_login(None, user)
        pp.pprint("logged in")
        pp.pprint(user.pk)
        pp.pprint(username)
        pp.pprint(password)
        token = account_activation_token.make_token(user)
        pp.pprint(token)
        user.is_active = True
        request.user = user
        pp.pprint(request.user)
        return Response({"status": status.HTTP_200_OK, "Token": token})

@method_decorator(csrf_exempt, name='post')
class SignupViewSet(APIView):
    permission_classes = [permissions.AllowAny]
    @csrf_exempt
    def post(self, request):
        #permission_classes = [permissions.IsAuthenticated]
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        #serializer.is_valid(raise_exception=True)
        #serializer.validate(data=request.data)
        username = request.data.get('username')
        password = request.data.get('password')	
        password2 = request.data.get('password2')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        authenticate(username=username, password=password, password2=password2, email=email)
        user = serializer.create(validated_data=request.data)
        user.refresh_from_db()
        #user.profile.birth_date = form.cleaned_data.get('birth_date')
        user.is_staff = False
        user.is_superuser = False
        user.is_admin = False
        user.save()
        #Profile.objects.create(user=user)
        user.profile.first_name = first_name
        user.profile.last_name = last_name
        user.profile.save()
        subject = 'Activate Your Lug Account'
        login(request, user)
        #user.email_user(subject, message)
        return HttpResponseRedirect('/profiles/')

permission_classes = [permissions.AllowAny]            
@method_decorator(csrf_exempt, name='post')
class LogoutViewSet(APIView):
    permission_classes = [permissions.AllowAny]
    @csrf_exempt
    def post(self, request):
        #permission_classes = [permissions.IsAuthenticated]
        #user = authenticate(username=username, password=password)
        pp = pprint.PrettyPrinter(indent=4)
        logout(request, request.user)
        pp.pprint("logged out")
        return HttpResponseRedirect('/profiles/')

class ProfileViewSet(APIView):
    
    queryset = Profile.objects.all()#permission_classes = (permissions.AllowAny,)
    serializer = ProfileSerializer(queryset, many=True)
    #permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        Profiles = Profile.objects.filter(user=request.user)
        serializer = ProfileSerializer(Profiles, many=True)
        return Response(serializer.data)

#@method_decorator(csrf_exempt, name='dispatch')
class PostViewSet(APIView):
    queryset = Post.objects.all()#permission_classes = (permissions.AllowAny,)
    serializer = PostSerializer(queryset, many=True)
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        form = PostForm(request.POST or None, request.FILES or None)
        permission_classes = [permissions.AllowAny]
        prepared_data_variable = request.user
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['Author'] = prepared_data_variable
            serializer.save()
        return Response(serializer.data)
   
    def put(self, request):
        form = PostForm(request.POST or None, request.FILES or None)
        serializer = PostSerializer(data=request.data)
        #serializer.data.LikeCount = 15
        #post.Likes.add(request.user)
        #post.LikeCount += 1
        if serializer.is_valid():
            serializer.data['LikeCount'] = 15
            serializer.save()
        return Response(serializer.data)	

class MessageViewSet(APIView):
    queryset = Message.objects.all()
    serializer = MessageSerializer(queryset, many=True)
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        #queryset = Profile.objects.all()
        permission_classes = [permissions.IsAuthenticated]
        messages = Message.objects.filter(Q(receiver=request.user))
        serializer = MessageSerializer(messages, many=True)
        prepared_data_variable = request.user
        return Response(serializer.data)

    def post(self, request):
        permission_classes = [permissions.IsAuthenticated]
        prepared_data_variable = request.user
        form = MessageForm(request.POST or None)
        serializer = MessageSerializer(data=request.data)
        #messages = Message.objects.filter(Q(receiver__username=request.user.username) | Q(sender__username=request.user.username))
        #receiver = serializer.receiver
        if serializer.is_valid():
            serializer.validated_data['sender'] = prepared_data_variable
            serializer.save()
        return Response(serializer.data)	

class NotificationViewSet(APIView):
    queryset = Notification.objects.all()
    serializer = NotificationSerializer(queryset, many=True)
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        #queryset = Profile.objects.all()
        permission_classes = [permissions.IsAuthenticated]
        notifications = Notification.objects.filter(receiver=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        prepared_data_variable = request.user
        return Response(serializer.data)
  
    def post(self, request):
        permission_classes = [permissions.IsAuthenticated]
        prepared_data_variable = request.user
        receiver = request.user
        serializer = NotificationSerializer(data=request.data)
        notifications = Message.objects.filter(receiver=request.user)
        if serializer.is_valid():
            serializer.validated_data['sender'] = prepared_data_variable
            serializer.save()
        return Response(serializer.data)

class JobDetailViewSet(APIView):
    queryset = Job.objects.all()#permission_classes = (permissions.AllowAny,)
    serializer = PostSerializer(queryset, many=True)
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        job_id = request.data.get('id')
        jobs = Job.objects.filter(Q(id=job_id))
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)

class AcceptJobViewSet(APIView):
    queryset = Job.objects.all()#permission_classes = (permissions.AllowAny,)
    serializer = PostSerializer(queryset, many=True)
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        job_id = self.request.GET.get('q', None)
        jobs = Job.objects.filter(Q(id=job_id))
        serializer = JobSerializer(jobs, many=True)
        assignJob(request, job_id)
        return Response(serializer.data)              

permission_classes = [permissions.AllowAny]
@method_decorator(csrf_exempt, name='post')   
class JobViewSet(APIView):
    queryset = Job.objects.all().order_by('Created').reverse()
    serializer = JobSerializer(queryset, many=True)
    
    def get(request, self):
        queryset = Job.objects.filter(InProgress=False).order_by('Created').reverse()
        serializer = JobSerializer(queryset, many=True)
        return Response(serializer.data)

    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = JobSerializer(data=request.data)
        
        if serializer.is_valid(): 
            serializer.save()
        return Response(serializer.data) 


permission_classes = [permissions.AllowAny]
@method_decorator(csrf_exempt, name='get')   
class AddJobViewSet(APIView):
    queryset = Job.objects.all().order_by('Created').reverse()
    serializer = JobSerializer(queryset, many=True)
    
    def get(self, request):
        job_id = self.request.GET.get('q', None)
        jobs = Job.objects.filter(Q(id=job_id))
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)           


permission_classes = [permissions.AllowAny]
@method_decorator(csrf_exempt, name='post')
class MyJobViewSet(APIView):
    queryset = Job.objects.all().order_by('Created').reverse()
    serializer = JobSerializer(queryset, many=True)
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        queryset = Job.objects.filter(Assigned_Lugger = request.user).order_by('Created').reverse()
        serializer = JobSerializer(queryset, many=True)
        return Response(serializer.data)
  
    def post(self, request):
        user = request.user
        serializer = JobSerializer(data=request.data)
        
        if serializer.is_valid():
            job_id = request.data.get('id')
            assignJob(job_id, user)
            return Response(serializer.data)    
        return Response(serializer.data)        
                               
class GroupViewSet(APIView):

    def get(self, request):
        #queryset = Profile.objects.all()
        groups = User_Groups.objects.filter(user=request.user)
        serializer = GroupSerializer(groups, many=True)
        prepared_data_variable = request.user
        return Response(serializer.data)


class TopicViewSet(APIView):

    def get(self, request):
        topics = Topic.objects.all()
        serializer = TopicSerializer(topics, many=True)
        return Response(serializer.data)

class ProfileBackend(object):

    def authenticate(self, username=None, password=None):
        stud = Profile.objects.filter(username=username)
        if stud.exists():
            if check_password(password, stud[0].password):
                return stud[0]
        return None
    def get_user(self, username):
        prof = Profile.objects.filter(username=username)
        if prof.exists():
            return prof[0]
        else:
            return None        	

#Content = form.save(commit=False)
        #Content.Author = request.user
        #files = request.FILES.getlist('Image')
        #fs = FileSystemStorage()
        #Content.save()
        #form = PostForm(request.POST or None, request.FILES or None, instance=Content)








