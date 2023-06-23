"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from django.conf.urls import include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from main import views
from main import views as core_views
from API import views as api_views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers
from django.views.decorators.csrf import csrf_exempt

#router = routers.DefaultRouter()
#router.register('', views.ProfileList.as_view()),


urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('', include('main.urls')),
    path('admin/', admin.site.urls), #path('admin_tools_stats/', include('admin_tools_stats.urls')),
    path('jobs/', views.JobViewSet.as_view()),
    path('add/', views.AddJobViewSet.as_view()),
    path('acceptjob/', views.AcceptJobViewSet.as_view()),
    path('getLocation/', views.LocationViewSet.as_view()),
    path('completejob/', views.CompleteJobViewSet.as_view()),
    path('checkout/', views.CheckoutSessionView.as_view()),
    path('create/', views.CreateStripeAccountView.as_view()),
    path('deposit/', views.TransferBalanceToStripeView.as_view()),
    path('myorders/', views.MyOrdersViewSet.as_view()),
    path('myjobs/', views.MyJobViewSet.as_view()),
    path('images/', views.ImageViewSet.as_view()),
    path('video/', views.VideoViewSet.as_view()),
    path('groups/', views.GroupViewSet.as_view()),
    path('logout/', views.signout, name='signout'),
    path('login/', views.LoginViewSet.as_view()),
    path('register/', views.SignupViewSet.as_view()),
    path('profiles/', views.ProfileViewSet.as_view()),
    path('lugger/', views.LuggerViewSet.as_view()),
    path('messages/', views.MessageThreadViewSet.as_view()),
    path('newmsg/', views.NewMessageViewSet.as_view()),
    path('topics/', views.TopicViewSet.as_view()),
    path('notifications/', views.NotificationViewSet.as_view()),
    path('posts/', views.PostViewSet.as_view()),
    path('main/', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('(<post_id>[0-9]+)/(<username>[a-zA-Z0-9]+)/DM/', views.DMPost, name='DMPost'),
    path('(<post_id>[0-9]+)/message/', views.message, name='message'),
    path('(<post_id>[0-9]+)/msg/', views.msg, name='msg'),
    path('(<username>[a-zA-Z0-9]+)/inbox/', views.inbox, name='inbox'),
    path('(<post_id>[0-9]+)/post/', views.post_detail, name='post_detail'),
    path('(<label>[a-zA-Z0-9]+)/topics/', views.topics, name='topics'),
    path('(<Repost_id>[0-9]+)/post/', views.repost_detail, name='repost_detail'),
    path('(<post_id>[0-9]+)/unrepost/', views.unrepost, name='unrepost'),
    path('(<post_id>[0-9]+)/(<username>[a-zA-Z0-9]+)/like/', views.like, name='like'),
    path('(<post_id>[0-9]+)/unlike/', views.unlike, name='unlike'),
    path('(<post_id>[0-9]+)/flag/', views.flag, name='flag'),
    path('group/', views.group, name='group'),
    path('account_activation_sent/', core_views.account_activation_sent, name='account_activation_sent'),
    path('activate/(<uidb64>[0-9A-Za-z_\-]+)/(<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
        core_views.activate, name='activate'),
    path('(<user_id>[0-9]+)/', views.user_profile, name='user_profile'),
    path('(<username>[a-zA-Z0-9]+)', views.get_user_profile, name='get_user_profile'),
    path('(<username>[a-zA-Z0-9]+)/go_private/', views.go_private, name='go_private'),
    path('(<username>[a-zA-Z0-9]+)/remove_private/', views.go_public, name='go_public'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('report/', views.report, name='report'),
    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = format_suffix_patterns(urlpatterns)     