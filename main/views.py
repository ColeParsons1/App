from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from sendsms import api
import math
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
from rest_framework_api_key.permissions import HasAPIKey
import json
import stripe
import geopy.distance
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models import Q
from django.template import loader
#from django.conf.urls import url
from django.contrib.contenttypes.fields import GenericForeignKey
from django.shortcuts import render, redirect
from .forms import sign
import datetime
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
from .serializers import TopicSerializer
from .serializers import LoginSerializer
from .serializers import RegisterSerializer
from .serializers import TemplateSerializer
from .serializers import VideoSerializer
from rest_framework import permissions
from functools import reduce
from .models import Topic
from .models import Post, Comment, Repost, Job, Liked_Post, Profile, Message, Notification, Flagged_Post, Images, Vid
from .forms import CommentForm
from .forms import PostForm
from .forms import ProfileForm, ImageForm, MessageForm, DMPostForm
from django.core.files.storage import FileSystemStorage
from django.views.generic import TemplateView, ListView
from django.utils.decorators import method_decorator
import json
from geopy.geocoders import Nominatim
import requests
import urllib.parse
from django.middleware.csrf import get_token


def index(request):
    User = get_user_model()
    users = User.objects.all()
    all_posts = Post.objects.all().order_by('Created').reverse()
    all_reposts = Repost.objects.all().order_by('Created').reverse()
    all_liked = Liked_Post.objects.all()
    com = Comment.objects.filter().count
    #following = Follow.objects.following(request.user)
    #default_pic = default_Profile_pic.objects.all()
    #post_list = zip(all_posts, all_reposts)
    form = PostForm(request.POST or None, request.FILES or None)
    dmForm = MessageForm(request.POST or None)
    #group_form = GroupForm(request.POST or None)
    Author = request.user
    
    if request.method == 'POST':
        if 'postFeed' in request.POST:
        #job = form.save(commit=False)
        
        #job.save()
        #form = PostForm(request.POST or None, instance=job)
        
        #form.save()

            Content = form.save(commit=False)
            Content.Author = request.user
            Content.Author_Profile = request.user.profile
            files = request.FILES.getlist('Image')
            fs = FileSystemStorage()
            Content.save()
            form = PostForm(request.POST or None, request.FILES or None, instance=Content)
            return HttpResponse('<script>history.back();</script>')
            
    else:
        form = PostForm()    
        dmForm = MessageForm()
        #group_form = GroupForm()
        
    context = {
        'User': users,
        'all_posts': all_posts,
        #'following': following,
        'form': form,
        'Author': Author,
        'all_reposts': all_reposts,
        'all_liked': all_liked,
        'dmForm': dmForm,
        #'group_form': group_form,
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
@method_decorator(csrf_exempt, name='updateLocation')
def updateLocation(request, lat, lon):
    permission_classes = [permissions.AllowAny]
    #job = get_object_or_404(Job, pk=job_id)
    usr = request.user
    usr.profile.lat = lat
    usr.profile.lon = lon
    usr.profile.save()


    return render(request=request, template_name="main/login.html", context={"login_form":usr})    
    

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

@csrf_exempt            
@method_decorator(csrf_exempt, name='completeJob')
def completeJob(request, job_id, completion_image):
    permission_classes = [permissions.AllowAny]
    job = get_object_or_404(Job, pk=job_id)
    usr = request.user
    job.InProgress = False
    job.CompletionImage = completion_image
    job.Complete = True
    balance = usr.profile.Balance
    payout = job.Driver_Pay
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(job_id)
    pp.pprint(payout)
    pp.pprint(balance)
    usr.profile.Balance = balance + payout
    usr.profile.save()
    pp.pprint(usr.profile.Balance)
    job.save()
    #sendNotification()

    return render(request=request, template_name="main/login.html", context={"login_form":job})    


def getDistance(request):
        lat_pickup_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+urllib.parse.quote(Pickup_Address)+'&key=AIzaSyBCTEHjteAUobF6e3tqcMnkZC-2cGBQSkU')
        resp_json_payload = lat_pickup_response.json()
        print(resp_json_payload['results'][0]['geometry']['location']['lat'])
        Latitude_Pickup = resp_json_payload['results'][0]['geometry']['location']['lat']
        lng_pickup_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+urllib.parse.quote(Pickup_Address)+'&key=AIzaSyBCTEHjteAUobF6e3tqcMnkZC-2cGBQSkU')
        resp_json_payload = lng_pickup_response.json()
        print(resp_json_payload['results'][0]['geometry']['location']['lat'])
        Longitude_Pickup = resp_json_payload['results'][0]['geometry']['location']['lng']

        lat_destination_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+urllib.parse.quote(Destination_Address)+'&key=AIzaSyBCTEHjteAUobF6e3tqcMnkZC-2cGBQSkU')
        resp_json_payload = lat_destination_response.json()
        print(resp_json_payload['results'][0]['geometry']['location']['lat'])
        Latitude_Destination = resp_json_payload['results'][0]['geometry']['location']['lat']
        lng_destination_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+urllib.parse.quote(Destination_Address)+'&key=AIzaSyBCTEHjteAUobF6e3tqcMnkZC-2cGBQSkU')
        resp_json_payload = lng_destination_response.json()
        print(resp_json_payload['results'][0]['geometry']['location']['lat'])
        Longitude_Destination = resp_json_payload['results'][0]['geometry']['location']['lng']

        coords_1 = (Latitude_Pickup, Longitude_Pickup)
        coords_2 = (Latitude_Destination, Longitude_Destination)
        Distance = geopy.distance.geodesic(coords_1, coords_2).miles 
        return Distance  


@csrf_exempt            
@method_decorator(csrf_exempt, name='addJobToSchedule')
def addJobToSchedule(request, job_id):
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
        pp.pprint(username)
        pp.pprint(password)
        #user = authenticate(username=username, password=password)
        user = User.objects.get(username='Test')
        pp = pprint.PrettyPrinter(indent=4)
        login(request, user)
        update_last_login(None, user)
        pp.pprint("logged in")
        pp.pprint(user.pk)
        pp.pprint(username)
        pp.pprint(password)
        token = '814ID5KoLNqmuObh2RbCXZ1VcG6laVmWrmaIS8EE9NYpBjd48JcXfZJeAG0P8eEs'#account_activation_token.make_token(user)
        pp.pprint(token)
        user.is_active = True
        request.user = user
        pp.pprint(request.user)
        user_logged_in.send(sender=user.__class__, request=request, user=user) 
        return render(request=request, template_name="main/login.html", context={"login_form":job})

        
    def get(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.validate(data=request.data)
        #username = request.data.get('username')
        
        username = self.request.GET.get('username', None)
        password = self.request.GET.get('password', None)
        pp.pprint(username)
        pp.pprint(password)
        #password = request.data.get('password')	
        user = authenticate(username=self.request.GET.get('username', None), password=self.request.GET.get('password', None))
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
        user.profile.Token = token
        user.profile.save()
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
        email = request.data.get('username')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        authenticate(username=username, password=password, password2=password2, email=username)
        user = serializer.create(validated_data=request.data)
        user.refresh_from_db()
        #user.profile.birth_date = form.cleaned_data.get('birth_date')
        user.is_staff = False
        user.is_superuser = False
        user.is_admin = False
        user.save()
        #login(request, user)
        #Profile.objects.create(user=user)
        user.profile.first_name = username
        user.profile.last_name = username
        user.profile.save()
        login(request, user)
        request.user = user
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(request.user)
        csrf_token = get_token(request)
        user.profile.Token = csrf_token
        user.profile.save()
        pp.pprint(csrf_token)
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

class LuggerViewSet(APIView):
    
    queryset = Profile.objects.all()#permission_classes = (permissions.AllowAny,)
    serializer = ProfileSerializer(queryset, many=True)
    #permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        assigned_lugger = self.request.GET.get('assignedlugger', None)
        #jobs = Pr.objects.filter(Q(user=job_i))
        Profiles = Profile.objects.filter(username=assigned_lugger)
        serializer = ProfileSerializer(Profiles, many=True)
        #pp = pprint.PrettyPrinter(indent=4)
        #csrf_token = get_token(request)
        #pp.pprint(csrf_token)
        return Response(serializer.data)        

class ProfileViewSet(APIView):
    
    queryset = Profile.objects.all()#permission_classes = (permissions.AllowAny,)
    serializer = ProfileSerializer(queryset, many=True)
    #permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        Profiles = Profile.objects.filter(user=request.user)
        serializer = ProfileSerializer(Profiles, many=True)
        pp = pprint.PrettyPrinter(indent=4)
        return Response(serializer.data)

#@method_decorator(csrf_exempt, name='dispatch')
class PostViewSet(APIView):
    queryset = Post.objects.all()#permission_classes = (permissions.AllowAny,)
    serializer = PostSerializer(queryset, many=True)
    #permission_classes = [permissions.IsAuthenticated]  
    permission_classes = [permissions.AllowAny]
    #permission_classes = [HasAPIKey]
    def get(self, request):
        #queryset = Profile.objects.all()
        #Author__contains=request.user.profile.User_Following
 
        viewer = request.user
            #return i
        #d = .aut                         
        posts = Post.objects.all().order_by('id').reverse()

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @csrf_exempt
    def post(self, request):
        form = PostForm(request.POST or None, request.FILES or None)
        prepared_data_variable = request.user  #and serializer.validated_data['IsRepost'] == False
        serializer = PostSerializer(data=request.data)
        pp = pprint.PrettyPrinter(indent=4)
        username = request.user.username
        user = request.user
        data = request.data
        Content = data.get('Content')
        checked = "My vibe has been checked :("

        if "enate" in Content.replace(" ", ""):
            Content = checked
        if "olitic" in Content.replace(" ", ""):
            Content = checked	
        if "limate" in Content.replace(" ", ""):
            Content = checked
        if "rump" in Content.replace(" ", ""):
            Content = checked
        if "police" in Content.replace(" ", ""):
            Content = checked
        if "elect" in Content.replace(" ", ""):
            Content = checked
        if "epublican" in Content.replace(" ", ""):
            Content = checked
        if "emocrat" in Content.replace(" ", ""):
            Content = checked
        if "Biden" in Content.replace(" ", ""):
            Content = checked
        if "acist" in Content.replace(" ", ""):
            Content = checked
        if "acism" in Content.replace(" ", ""):
            Content = checked
        if "ropaganda" in Content.replace(" ", ""):
            Content = checked
        if "emocracy" in Content.replace(" ", ""):
            Content = checked
        if "racial" in Content.replace(" ", ""):
            Content = checked
        if "acial" in Content.replace(" ", ""):
            Content = checked    
        if "rivelage" in Content.replace(" ", ""):
            Content = checked
        if "hite" in Content.replace(" ", ""):
            Content = checked
        if "lave" in Content.replace(" ", ""):
            Content = checked
        if "BLM" in Content.replace(" ", ""):
            Content = checked
        if "blm" in Content.replace(" ", ""):
            Content = checked
        if "lack lives matter" in Content.replace(" ", ""):
            Content = checked
        if "president" in Content.replace(" ", ""):
            Content = checked
        if "vote" in Content.replace(" ", ""):
            Content = checked
        if "GOP" in Content.replace(" ", ""):
            Content = checked
        if "upreme court" in Content.replace(" ", ""):
            Content = checked
        if "KKK" in Content.replace(" ", ""):
            Content = checked
        if "ongress" in Content.replace(" ", ""):
            Content = checked
        if "apitol" in Content.replace(" ", ""):
            Content = checked
        if "law" in Content.replace(" ", ""):
            Content = checked
        if "tax" in Content.replace(" ", ""):
            Content = checked
        if "DNC" in Content.replace(" ", ""):
            Content = checked
        if "RNC" in Content.replace(" ", ""):
            Content = checked
        if "andidate" in Content.replace(" ", ""):
            Content = checked
        if "CNN" in Content.replace(" ", ""):
            Content = checked
        if "olice" in Content.replace(" ", ""):
            Content = checked
        if "fficer" in Content.replace(" ", ""):
            Content = checked
        if "enator" in Content.replace(" ", ""):
            Content = checked
        if "overn" in Content.replace(" ", ""):
            Content = checked
        if "onstitution" in Content.replace(" ", ""):
            Content = checked
        if "NRA" in Content.replace(" ", ""):
            Content = checked
        if "nra" in Content.replace(" ", ""):
            Content = checked
        if "kkk" in Content.replace(" ", ""):
            Content = checked
        if "ealthcare" in Content.replace(" ", ""):
            Content = checked
        if "mendmant" in Content.replace(" ", ""):
            Content = checked
        if "gun" in Content.replace(" ", ""):
            Content = checked
        if "ilibuster" in Content.replace(" ", ""):
            Content = checked
        if "hite house" in Content.replace(" ", ""):
            Content = checked
        if "hite House" in Content.replace(" ", ""):
            Content = checked
        if "ederal" in Content.replace(" ", ""):
            Content = checked
        if "QAnon" in Content.replace(" ", ""):
            Content = checked
        if "ovid" in Content.replace(" ", ""):
            Content = checked
        if "accin" in Content.replace(" ", ""):
            Content = checked
        if "ommunis" in Content.replace(" ", ""):
            Content = checked
        if "Asian" in Content.replace(" ", ""):
            Content = checked
        if "union" in Content.replace(" ", ""):
            Content = checked
        if "tudent debt" in Content.replace(" ", ""):
            Content = checked
        if "tudent Debt" in Content.replace(" ", ""):
            Content = checked
        if "rotest" in Content.replace(" ", ""):
            Content = checked
        if "orporation" in Content.replace(" ", ""):
            Content = checked
        if "ight wing" in Content.replace(" ", ""):
            Content = checked
        if "eft wing" in Content.replace(" ", ""):
            Content = checked
        if "ight-wing" in Content.replace(" ", ""):
            Content = checked
        if "eft-wing" in Content.replace(" ", ""):
            Content = checked 
        if "mmigrant" in Content.replace(" ", ""):
            Content = checked
        if "edicare" in Content.replace(" ", ""):
            Content = checked
        if "edicaid" in Content.replace(" ", ""):
            Content = checked
        if "ecretary" in Content.replace(" ", ""):
            Content = checked
        if "ilitary" in Content.replace(" ", ""):
            Content = checked
        if "Obama" in Content.replace(" ", ""):
            Content = checked
        if "obama" in Content.replace(" ", ""):
            Content = checked
        if "un control" in Content.replace(" ", ""):
            Content = checked
        if "azi" in Content.replace(" ", ""):
            Content = checked
        if "iot" in Content.replace(" ", ""):
            Content = checked
        if "USDA" in Content.replace(" ", ""):
            Content = checked
        if "usda" in Content.replace(" ", ""):
            Content = checked
        if "FDA" in Content.replace(" ", ""):
            Content = checked
        if "fda" in Content.replace(" ", ""):
            Content = checked
        if "ascis" in Content.replace(" ", ""):
            Content = checked
        if "harma" in Content.replace(" ", ""):
            Content = checked
        if "FBI" in Content.replace(" ", ""):
            Content = checked
        if "Tax" in Content.replace(" ", ""):
            Content = checked
        if "uthoritarian" in Content.replace(" ", ""):
            Content = checked
        if "olitician" in Content.replace(" ", ""):
            Content = checked
        if "onservative" in Content.replace(" ", ""):
            Content = checked
        if "uslim" in Content.replace(" ", ""):
            Content = checked
        if "lection" in Content.replace(" ", ""):
            Content = checked
        if "hristian" in Content.replace(" ", ""):
            Content = checked
        if "arxis" in Content.replace(" ", ""):
            Content = checked
        if "narch" in Content.replace(" ", ""):
            Content = checked
        if "OVID" in Content.replace(" ", ""):
            Content = checked
        if "oronavirus" in Content.replace(" ", ""):
            Content = checked
        if "elhi" in Content.replace(" ", ""):
            Content = checked
        if "media" in Content.replace(" ", ""):
            Content = checked
        if "Media" in Content.replace(" ", ""):
            Content = checked
        if "United States" in Content.replace(" ", ""):
            Content = checked
        if "hreat" in Content.replace(" ", ""):
            Content = checked
        if "AOC" in Content.replace(" ", ""):
            Content = checked
        if "aoc" in Content.replace(" ", ""):
            Content = checked
        if "God " in Content.replace(" ", ""):
            Content = checked
        if "ibertarian" in Content.replace(" ", ""):
            Content = checked
        if "iberal" in Content.replace(" ", ""):
            Content = checked
        if "1A" in Content.replace(" ", ""):
            Content = checked
        if "2A" in Content.replace(" ", ""):
            Content = checked
        if "saki" in Content.replace(" ", ""):
            Content = checked
        if "order" in Content.replace(" ", ""):
            Content = checked
        if "un control" in Content.replace(" ", ""):
            Content = checked
        if "eftist" in Content.replace(" ", ""):
            Content = checked
        if "mpeach" in Content.replace(" ", ""):
            Content = checked
        if "ountry" in Content.replace(" ", ""):
            Content = checked
        if "ountries" in Content.replace(" ", ""):
            Content = checked
        if "partisan" in Content.replace(" ", ""):
            Content = checked
        if "Partisan" in Content.replace(" ", ""):
            Content = checked
        if "lobal" in Content.replace(" ", ""):
            Content = checked
        if "auci" in Content.replace(" ", ""):
            Content = checked
        if "Cox" in Content.replace(" ", ""):
            Content = checked
        if "reen party" in Content.replace(" ", ""):
            Content = checked
        if "reen Party" in Content.replace(" ", ""):
            Content = checked
        if "ncap" in Content.replace(" ", ""):
            Content = checked
        if "rexit" in Content.replace(" ", ""):
            Content = checked
        if "onfederate" in Content.replace(" ", ""):
            Content = checked
        if "flag" in Content.replace(" ", ""):
            Content = checked
        if "IRS" in Content.replace(" ", ""):
            Content = checked
        if "ardon" in Content.replace(" ", ""):
            Content = checked
        if "Build Back Better" in Content.replace(" ", ""):
            Content = checked
        if "uild back better" in Content.replace(" ", ""):
            Content = checked
        if "nigge" in Content.replace(" ", ""):
            Content = checked
        if "Nigge" in Content.replace(" ", ""):
            Content = checked    
        if "range man" in Content.replace(" ", ""):
            Content = checked
        if "range Man" in Content.replace(" ", ""):
            Content = checked
        if "hristian" in Content.replace(" ", ""):
            Content = checked
        if "ewish" in Content.replace(" ", ""):
            Content = checked
        if "Jew" in Content.replace(" ", ""):
            Content = checked
        if "jew" in Content.replace(" ", ""):
            Content = checked
        if "Jesus do" in Content.replace(" ", ""):
            Content = checked
        if "Jesus said" in Content.replace(" ", ""):
            Content = checked
        if "ace theory" in Content.replace(" ", ""):
            Content = checked
        if "ace Theory" in Content.replace(" ", ""):
            Content = checked
        if "ar on Drugs" in Content.replace(" ", ""):
            Content = checked
        if "ar on drugs" in Content.replace(" ", ""):
            Content = checked
        if "leepy Joe" in Content.replace(" ", ""):
            Content = checked
        if "leepy joe" in Content.replace(" ", ""):
            Content = checked
        if "aetz" in Content.replace(" ", ""):
            Content = checked
        if "allot" in Content.replace(" ", ""):
            Content = checked
        if "stablish" in Content.replace(" ", ""):
            Content = checked
        if "he news" in Content.replace(" ", ""):
            Content = checked
        if "ox news" in Content.replace(" ", ""):
            Content = checked
        if "ox News" in Content.replace(" ", ""):
            Content = checked
        if "ransphob" in Content.replace(" ", ""):
            Content = checked
        if " rights" in Content.replace(" ", ""):
            Content = checked
        if "Rights" in Content.replace(" ", ""):
            Content = checked
        if "egulat" in Content.replace(" ", ""):
            Content = checked
        if "ender" in Content.replace(" ", ""):
            Content = checked
        if "olocaust" in Content.replace(" ", ""):
            Content = checked
        if "eminis" in Content.replace(" ", ""):
            Content = checked
        if "elfare" in Content.replace(" ", ""):
            Content = checked
        if "hapiro" in Content.replace(" ", ""):
            Content = checked
        if "ucker Carlson" in Content.replace(" ", ""):
            Content = checked
        if "ucker carlson" in Content.replace(" ", ""):
            Content = checked
        if "itch Mcconnel" in Content.replace(" ", ""):
            Content = checked
        if "itler" in Content.replace(" ", ""):
            Content = checked
        if "anon" in Content.replace(" ", ""):
            Content = checked
        if "eagan" in Content.replace(" ", ""):
            Content = checked
        if " war" in Content.replace(" ", ""):
            Content = checked
        if "War " in Content.replace(" ", ""):
            Content = checked
        if "ussia" in Content.replace(" ", ""):
            Content = checked
        if "nvade" in Content.replace(" ", ""):
            Content = checked
        if "roops" in Content.replace(" ", ""):
            Content = checked
        if "WW3" in Content.replace(" ", ""):
            Content = checked
        if "ar 3" in Content.replace(" ", ""):
            Content = checked
        if "ar III" in Content.replace(" ", ""):
            Content = checked
        if "WWIII" in Content.replace(" ", ""):
            Content = checked
        if "JB" in Content.replace(" ", ""):
            Content = checked
        if "jb" in Content.replace(" ", ""):
            Content = checked
        if "left" in Content.replace(" ", ""):
            Content = checked
        if "Left" in Content.replace(" ", ""):
            Content = checked		
        if Content == checked:
            Content.delete()												
        else:
            Content = Content
        if serializer.is_valid():
            if serializer.validated_data['IsRepost'] != True and serializer.validated_data['IsLike'] == False and serializer.validated_data['IsComment'] == False:
                serializer.validated_data['Author'] = prepared_data_variable
                serializer.validated_data['Author_Profile'] = request.user.profile
                serializer.validated_data['Content'] = Content
                serializer.validated_data['Image'] = serializer.validated_data['ImageString']
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

class MessageThreadViewSet(APIView):
	queryset = Message.objects.all()
	serializer = MessageSerializer(queryset, many=True)
	permission_classes = [permissions.AllowAny]
	def get(self, request):
		#queryset = Profile.objects.all()
		User = get_user_model()
		#user = User.objects.get(username=username)
		messages = Message.objects.filter(Q(receiver__username=request.user.username) | Q(sender__username=request.user.username)).order_by('created_at')
		permission_classes = [permissions.AllowAny]
		#messages = Message.objects.filter(Q(receiver__username=request.user.username)).order_by('created_at').reverse()
		serializer = MessageSerializer(messages, many=True)
		prepared_data_variable = request.user
		return Response(serializer.data)

	def post(self, request):
		permission_classes = [permissions.AllowAny]
		prepared_data_variable = request.user
		form = MessageForm(request.POST or None)
		serializer = MessageSerializer(data=request.data)
		data = request.data
		#User = get_user_model()
		
		receiverName = data.get('receiver')
		receiverUser = User.objects.get(username=request.user.username)

		#self.get(self, request, )
		messages = Message.objects.filter(Q(receiver__username=request.user.username) | Q(sender__username=request.user.username))
		#receiver = serializer.receiver
		data = request.data
		#User = get_user_model()
		return Response(serializer.data)

class NewMessageViewSet(APIView):
    queryset = Message.objects.all()#permission_classes = (permissions.AllowAny,)
    serializer = MessageSerializer(queryset, many=True)
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        Receiver = self.request.GET.get('receiver', None).replace("_", " ")
        Content = self.request.GET.get('msg_content', None).replace("_", " ")
        ImageString = self.request.GET.get('ImageString', None)
        j = self.request.GET.get('job', None)
        currentJob = get_object_or_404(Job, pk=j)
        receiverUser = User.objects.get(username=Receiver)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(Content)
        Message.objects.create(job=currentJob, sender=request.user, receiver=receiverUser, msg_content=Content, ImageString=ImageString, Image=ImageString)
        return Response()              

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

class LocationViewSet(APIView):
    queryset = Profile.objects.all()#permission_classes = (permissions.AllowAny,)
    serializer = ProfileSerializer(queryset, many=True)
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        queryset = Profile.objects.all()
        serializer = ProfileSerializer(queryset, many=True)
        lat = self.request.GET.get('lat', None)
        lon = self.request.GET.get('lon', None)
        updateLocation(request, lat, lon)
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

class CompleteJobViewSet(APIView):
    queryset = Job.objects.all()#permission_classes = (permissions.AllowAny,)
    serializer = PostSerializer(queryset, many=True)
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        job_id = self.request.GET.get('id', None)
        completion_image = self.request.GET.get('CompletionImage', None)
        jobs = Job.objects.filter(Q(id=job_id))
        serializer = JobSerializer(jobs, many=True)
        completeJob(request, job_id, completion_image)
        return Response(serializer.data)                     

permission_classes = [permissions.AllowAny]
@method_decorator(csrf_exempt, name='post')   
class JobViewSet(APIView):
    queryset = Job.objects.filter(Q(Complete = False) & Q(InProgress = False)).order_by('Created').reverse()
    serializer = JobSerializer(queryset, many=True)
    
    def get(request, self):
        queryset = Job.objects.filter(Q(Complete = False) & Q(InProgress = False)).order_by('Created').reverse()
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
        Business_Name = self.request.GET.get('BusinessName', None).replace("_", " ")
        Job_Type = self.request.GET.get('JobType', None)
        Load_Weight = int(self.request.GET.get('LoadWeight', None))
        Length = self.request.GET.get('Length', None).replace(".0", "")
        Width = self.request.GET.get('Width', None).replace(".0", "")
        Height = self.request.GET.get('Height', None).replace(".0", "")
        ImageString = self.request.GET.get('ImageString', None)
        Pieces = self.request.GET.get('Pieces', None)
        Pickup_Address = self.request.GET.get('PickupAddress', None).replace("_", " ")
        Destination_Address = self.request.GET.get('DestinationAddress', None).replace("_", " ")
        Time_Needed = self.request.GET.get('TimeNeeded', None).replace("_", " ")
        Description = self.request.GET.get('Description', None).replace("_", " ")
        Tip = float(self.request.GET.get('Tip', None))
        PhoneNumber = self.request.GET.get('PhoneNumber', None)

        #DN = Date_Needed[:10]
        TN = Time_Needed[:19]

        L = int(Length)
        W = int(Width)
        H = int(Height)
        Wght = int(Load_Weight)

        type = Topic.objects.get(Label=Job_Type)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(Business_Name)
        pp.pprint(Job_Type)
        pp.pprint(Load_Weight)
        pp.pprint(Pieces)
        pp.pprint(Pickup_Address)
        pp.pprint(Destination_Address)
        pp.pprint(Description)
        pp.pprint(Tip)

        lat_pickup_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+urllib.parse.quote(Pickup_Address)+'&key=AIzaSyBCTEHjteAUobF6e3tqcMnkZC-2cGBQSkU')
        resp_json_payload = lat_pickup_response.json()
        print(resp_json_payload['results'][0]['geometry']['location']['lat'])
        Latitude_Pickup = resp_json_payload['results'][0]['geometry']['location']['lat']
        lng_pickup_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+urllib.parse.quote(Pickup_Address)+'&key=AIzaSyBCTEHjteAUobF6e3tqcMnkZC-2cGBQSkU')
        resp_json_payload = lng_pickup_response.json()
        print(resp_json_payload['results'][0]['geometry']['location']['lat'])
        Longitude_Pickup = resp_json_payload['results'][0]['geometry']['location']['lng']

        lat_destination_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+urllib.parse.quote(Destination_Address)+'&key=AIzaSyBCTEHjteAUobF6e3tqcMnkZC-2cGBQSkU')
        resp_json_payload = lat_destination_response.json()
        print(resp_json_payload['results'][0]['geometry']['location']['lat'])
        Latitude_Destination = resp_json_payload['results'][0]['geometry']['location']['lat']
        lng_destination_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+urllib.parse.quote(Destination_Address)+'&key=AIzaSyBCTEHjteAUobF6e3tqcMnkZC-2cGBQSkU')
        resp_json_payload = lng_destination_response.json()
        print(resp_json_payload['results'][0]['geometry']['location']['lat'])
        Longitude_Destination = resp_json_payload['results'][0]['geometry']['location']['lng']

        coords_1 = (Latitude_Pickup, Longitude_Pickup)
        coords_2 = (Latitude_Destination, Longitude_Destination)
        Distance = geopy.distance.geodesic(coords_1, coords_2).miles

        if (L <= 5) | (W <= 4) | (H <= 4) | (Wght <= 200):
            Price = (3.01 * Distance) #+ (Tip)
            Driver_Pay = (1.41 * Distance) #+ (Tip)
        if (L >= 6) | (W >= 5 & H >= 4) | (Wght >= 200):
            Price = (4.02 * Distance) #+ (Tip)
            Driver_Pay = (1.88 * Distance) #+ (Tip)

        #if (L >= 6) | (W >= 6) | (H >= 5) | (Wght >= 400):
            #Price = 4.20 * Distance
            #Driver_Pay = 1.97 * Distance


        #Car
        #if (L <= 3) | (W <= 3.4) | (H <= 2.2) | (Wght <= 250):
            #Price = 3 * Distance
            #Driver_Pay = 1.41 * Distance


#Small SUV
        #if (L >= 60”) | (W >= 3 & H >= 2.8)  | (Wght >= 400):
            #Price = 4.02 * Distance
            #Driver_Pay = 1.88 * Distance


#Standard SUV
        #if (L >= 62) or (W >= 48”and H >= 33) or (Wght >= 450):
            #Price = 4.02 * Distance
            #Driver_Pay = 1.88 * Distance



#Pickup Truck Short Bed
        #if (L >= 68) or (W >= 65) or (H >= 84) or (Wght >= 600):
            #Price = 4.20 * Distance
            #Driver_Pay = 1.97 * Distance

#Pickup Truck Standard Short Bed
        #if (L >= 77) or (W >= 65) or (H >= 84) or (Wght >= 600):
            #Price = 4.20 * Distance
            #Driver_Pay = 1.97 * Distance

#Pickup Truck Standard Long Bed
        #if (L >= 84) or (W >= 65) or (H >= 84) or (Wght >= 600):
            #Price = 4.20 * Distance
            #Driver_Pay = 1.97 * Distance

#Pickup Truck Standard Long Bed
        #if (L >= 96) or (W >= 65) or (H >= 84) or (Wght >= 600):
            #Price = 4.20 * Distance
            #Driver_Pay = 1.97 * Distance    

        Profit = Price - Driver_Pay

        fee = Price*0.029

        pp.pprint(Price)
        

        final_price = Price // 1 ** (int(math.log(Price, 10)) - 2 + 1) + fee
        #final_price = Price // 10 ** (int(math.log(Price, 10)) - 2 + 1) + fee
        pp.pprint(final_price)


        #Price = 3.02 * Distance
        #total = Price

        Job.objects.create(Business_Name=Business_Name, Author=request.user, Job_Type=type, Load_Weight=Load_Weight, Length=Length, Width=Width, Height=Height, ImageString=ImageString, Image=ImageString, CompletionImage="nil", Pieces=Pieces, Description=Description, Pickup_Address=Pickup_Address, Destination_Address=Destination_Address, Time_Needed=TN, Latitude_Pickup=Latitude_Pickup, Longitude_Pickup=Longitude_Pickup, Latitude_Destination=Latitude_Destination, Longitude_Destination=Longitude_Destination, Distance=Distance, Tip=Tip, Phone_Number=PhoneNumber, Price=round(final_price,2), Driver_Pay=round(Driver_Pay + Tip, 2), Profit=round(Profit, 2))
        #Business_Name = Job.objects.filter(Q(Business_Name=Business_Name))
        #Job_Type = Job.objects.filter(Q(Job_Type=Job_Type))
        return Response()           

permission_classes = [permissions.AllowAny]
@method_decorator(csrf_exempt, name='get')
class MyOrdersViewSet(APIView):
    queryset = Job.objects.all().order_by('Created').reverse()
    serializer = JobSerializer(queryset, many=True)
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        queryset = Job.objects.filter(Q(Author = request.user)).order_by('Time_Needed')
        serializer = JobSerializer(queryset, many=True)
        return Response(serializer.data)

permission_classes = [permissions.AllowAny]
@method_decorator(csrf_exempt, name='post')
class MyJobViewSet(APIView):
    queryset = Job.objects.all().order_by('Created').reverse()
    serializer = JobSerializer(queryset, many=True)
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        queryset = Job.objects.filter(Q(Assigned_Lugger = request.user) | Q(Author = request.user)).order_by('Created').reverse()
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


class VideoViewSet(APIView):
	queryset = Vid.objects.all()
	permission_classes = [permissions.AllowAny]
	serializer = VideoSerializer(queryset, many=True)
	@csrf_exempt
	def post(self, request):
		#post = Meme.objects.all()
		#prepared_data_variable = request.user
		serializer = VideoSerializer(data=request.data)
		#messages = Message.objects.filter(Q(receiver__username=request.user.username) | Q(sender__username=request.user.username))
		#receiver = serializer.receiver
		if serializer.is_valid():
			serializer.save()
		return Response(serializer.data)


permission_classes = [permissions.AllowAny]
@method_decorator(csrf_exempt, name='post')
class ImageViewSet(APIView):
    queryset = Images.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer = TemplateSerializer(queryset, many=True)

    @csrf_exempt
    def get(self, request):
        queryset = Images.objects.all()
        serializer = TemplateSerializer(data=request.data)
        I = self.request.GET.get('Image', None)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(I)
        Images.objects.create(Image = I)
        return Response(serializer.data)
    @csrf_exempt
    def post(self, request):
        #post = Meme.objects.all()
        #prepared_data_variable = request.user
        serializer = TemplateSerializer(data=request.data)
        #I = request.data.GET.get('Image', None)
        #Images.objects.create(Image = I)
        #messages = Message.objects.filter(Q(receiver__username=request.user.username) | Q(sender__username=request.user.username))
        #receiver = serializer.receiver
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)  

class CreateStripeAccountView(View):
    def post(self, request, *args, **kwargs):
        stripe.api_key = 'sk_test_51M1yvHABMyiljblNlxgjC76jKwkn5GCWjdBruPz2VWfESIgdBqaJvMqvwQ5F0H1Gt7zF2TnlYRWZNVEpKmcbcRNd00y0elqhRX'
        req_json = json.loads(request.body)
        customer = stripe.Customer.create(name='Cole', email='coleparsons22@gmail.com')
        #stripe.Customer.create(
        #description="My First Test Customer (created for API docs at https://www.stripe.com/docs/api)",
        #)
        #transfer = stripe.Transfer.create(
        #amount=1000,
        #currency="usd",
        #destination='{{CONNECTED_ACCOUNT_ID}}',
        #)

        CONNECTED_ACCOUNT_ID = customer.id

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(customer.id)
        
        account = stripe.Account.create(
        country="US",
        type="custom",
        capabilities={"card_payments": {"requested": True}, "transfers": {"requested": True}},
        )


        created_account=stripe.AccountLink.create(
        account=account,
        refresh_url="https://connect.stripe.com/setup/c/acct_1McCyDPFYkUxcAmf/hTI7slJeP10O",
        return_url="https://dashboard.stripe.com/login",
        type="account_onboarding",
        )
        user = request.user
        user.profile.Stripe_Link = created_account.url
        user.profile.Stripe_Customer_ID = customer.id
        user.profile.Stripe_Account_ID = account.id
        user.profile.save()

        pp.pprint(created_account.url)
        pp.pprint(account.id)
        pp.pprint(created_account)
        pp.pprint(account)
        return JsonResponse({'url':created_account.url})


class TransferBalanceToStripeView(View):
    def post(self, request, *args, **kwargs):
        
        stripe.api_key = 'sk_test_51M1yvHABMyiljblNlxgjC76jKwkn5GCWjdBruPz2VWfESIgdBqaJvMqvwQ5F0H1Gt7zF2TnlYRWZNVEpKmcbcRNd00y0elqhRX'
        req_json = json.loads(request.body)

        balance=json.loads(request.body)['items'][0]['balance']
        id=json.loads(request.body)['items'][0]['id']

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(id)

        

        m = stripe.Account.modify(
        id,
        business_type="individual",
        individual={"first_name":"Cole", "last_name":"Parsons", "phone":"8288967682", "email":"coleparsons22@gmail.com", "id_number": "241836010", "dob[day]":"03", "dob[month]":"05", "dob[year]":"1996", "ssn_last_4":"6010", "address[line1]":"2088 Rock Springs Circle", "address[city]":"Denver", "address[state]":"NC", "address[postal_code]":"28037"},
        business_profile={"mcc": 4215, "url": "https://www.linkedin.com/in/cole-parsons-774221178/"},
        tos_acceptance={"date": 1609798905, "ip": "8.8.8.8"}
        )

        #'individual.address.city',
                                            # 'individual.address.line1', "address":"2088 Rock Springs Circle, Denver NC 28037"
                                            # 'individual.address.postal_code',
                                            # 'individual.address.state',
                                            # 'individual.dob.day',
                                            # 'individual.dob.month',
                                            # 'individual.dob.year',
                                            # 'individual.email',
                                            # 'individual.last_name',
                                            # 'individual.phone',
                                            # 'individual.ssn_last_4'],



        modify = stripe.Account.modify(
        id,
        capabilities={
        "transfers": {"requested": True}
        }
        )

        cap = stripe.Account.retrieve_capability(id, "transfers")

        pp.pprint(cap)

        p = str(balance*100)

        total = p.replace(".0", "")
        t2=total[ 0 : 3 ]

        transfer = stripe.Transfer.create(
        amount=t2,
        currency="usd",
        destination=id,
        )
        
        return JsonResponse({'url':m})                     	


class CheckoutSessionView(View):
    permission_classes = [HasAPIKey]
    def post(self, request, *args, **kwargs):
        permission_classes = [HasAPIKey]
        stripe.api_key = 'sk_test_51M1yvHABMyiljblNlxgjC76jKwkn5GCWjdBruPz2VWfESIgdBqaJvMqvwQ5F0H1Gt7zF2TnlYRWZNVEpKmcbcRNd00y0elqhRX'
        req_json = json.loads(request.body)
        customer = stripe.Customer.create(name='Cole', email='coleparsons22@gmail.com')
        #serializer = JobSerializer(data=request.data)
        #if serializer.is_valid():
            #product_id = request.data.get('id')
        product_id=json.loads(request.body)['items'][0]['id']#req_json["items"]["id"]   
        #product_id = self.request.GET.get('id')
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(product_id)
        #product_id = self.kwargs["id"]#112#serializer.data.get('id')#self.kwargs["pk"]
        #Business_Name = self.request.GET.get('BusinessName', None).replace("_", " ")
        product = Job.objects.get(id=product_id)
        added = product.Price + product.Tip
        p = str(added*100)
        pp.pprint(p)
        total = p.replace(".0", "")
        t2=total[ 0 : 3 ]
        pp.pprint(total)
        YOUR_DOMAIN = "http://146.190.222.176:8000"
        checkout_session = stripe.checkout.Session.create(
                success_url=YOUR_DOMAIN + '/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=YOUR_DOMAIN + '/cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': t2,
                        'product_data': {
                            'name': customer.name,
                            # 'images': ['https://i.imgur.com/EHyR2nP.png'],
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "product_id": product.id
            }

            )
        ephemeralKey = stripe.EphemeralKey.create(
        customer=customer['id'],
        stripe_version='2022-08-01',
        )    
        intent = stripe.PaymentIntent.create(
                amount=total,    #product.price,
                currency='usd',
                customer=customer['id'],
                automatic_payment_methods={
                    'enabled': True,
                },
                metadata={
                    "product_id": product.id
                }
            )
        return JsonResponse({'paymentIntent':intent.client_secret,
                 'ephemeralKey':ephemeralKey.secret,
                 'customer':customer.id,
                 'publishableKey':'sk_test_51M1yvHABMyiljblNlxgjC76jKwkn5GCWjdBruPz2VWfESIgdBqaJvMqvwQ5F0H1Gt7zF2TnlYRWZNVEpKmcbcRNd00y0elqhRX'}) #JsonResponse({'intentClientSecret': intent['client_secret']})

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        customer_email = session["customer_details"]["email"]
        product_id = session["metadata"]["product_id"]

        product = Job.objects.get(id=product_id)

        send_mail(
            subject="Here is your product",
            message=f"Thanks for your purchase. Here is the product you ordered. The URL is {product.url}",
            recipient_list=[customer_email],
            from_email="matt@test.com"
        )

        # TODO - decide whether you want to send the file or the URL
    
    elif event["type"] == "payment_intent.succeeded":
        intent = event['data']['object']

        stripe_customer_id = intent["customer"]
        stripe_customer = stripe.Customer.retrieve(stripe_customer_id)

        customer_email = stripe_customer['email']
        product_id = intent["metadata"]["product_id"]

        product = Job.objects.get(id=product_id)

        send_mail(
            subject="Here is your product",
            message=f"Thanks for your purchase. Here is the product you ordered. The URL is {product.url}",
            recipient_list=[customer_email],
            from_email="matt@test.com"
        )

    return HttpResponse(status=200)

@csrf_exempt
class StripeIntentView(View):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            req_json = json.loads(request.body)
            customer = stripe.Customer.create(email=req_json['email'])
            product_id = self.kwargs["pk"]
            product = Job.objects.get(id=product_id)
            
            intent = stripe.PaymentIntent.create(
                amount=product.price,
                currency='usd',
                customer=customer['id'],
                metadata={
                    "product_id": product.id
                }
            )
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({ 'error': str(e) })        









