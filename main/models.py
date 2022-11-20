from __future__ import division, unicode_literals
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
#from .forms import PostForm
#from .forms import CommentForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from warnings import warn
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count, Sum
#from star_ratings.models import UserRatingManager
#from star_ratings.models import RatingManager
#from star_ratings.models import UserRating
#from star_ratings.models import Rating
#from star_ratings.models import AbstractBaseRating

import uuid



class Topic(models.Model):
    Label = models.CharField(max_length=50)
    
    def __str__(self):
       return self.Label

class Vehicle_Type(models.Model):
    Label = models.CharField(max_length=50)
    
    def __str__(self):
       return self.Label

class Account_Type(models.Model):
    Label = models.CharField(max_length=50)
    
    def __str__(self):
       return self.Label       



class Job(models.Model):
    Author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="auth")
    Business_Name = models.CharField(max_length=300, default=uuid.uuid1)
    Business_Profile_Picture = models.ImageField(blank=True, null=True)
    Job_Type = models.ForeignKey(Topic, on_delete=models.CASCADE, blank=True, null=True, related_name="Type")
    Description = models.CharField(max_length=300, default=uuid.uuid1)
    Load_Weight = models.PositiveIntegerField(default=0)
    Pieces = models.PositiveIntegerField(default=0)
    Size_Of_Vehicle_Needed = models.ForeignKey(Vehicle_Type, on_delete=models.CASCADE, blank=True, null=True, related_name="Vehicle")
    Image = models.ImageField(blank=True, null=True)
    ImageString = models.CharField(max_length=300, default=uuid.uuid1)
    Pickup_Address = models.CharField(max_length=300, default=uuid.uuid1)
    Destination_Address = models.CharField(max_length=300, default=uuid.uuid1)
    Date_Needed = models.DateField(null=True, blank=True)
    Tip = models.FloatField(max_length=10, default=0.00)
    Latitude_Pickup = models.FloatField(max_length=300, blank=True, null=True)
    Longitude_Pickup = models.FloatField(max_length=300, blank=True, null=True)
    Latitude_Destination = models.FloatField(max_length=300, blank=True, null=True)
    Longitude_Destination = models.FloatField(max_length=300, blank=True, null=True)
    Distance = models.FloatField(max_length=300, default=1)
    Created = models.DateTimeField(auto_now_add=True)
    InProgress = models.BooleanField(default=False)
    Complete = models.BooleanField(default=False)
    Assigned_Lugger = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    slug = models.SlugField(
        default='',
        editable=False,
        max_length=75,
    )
    
    def __str__(self): 
        return self.Description


class User_Groups(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    Label = models.CharField(max_length=50)
    Members = models.ManyToManyField(User, blank=True, related_name="members")
    
    def __unicode__(self):
       return self.Label     
       

class Post(models.Model):
    Author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    Author_Profile = models.ForeignKey('main.Profile', on_delete=models.CASCADE, blank=True, null=True)
    Author_Profile_Picture = models.CharField(max_length=300, blank=True, null=True)
    Topic = models.ForeignKey(Topic, on_delete=models.CASCADE, blank=True, null=True, related_name="Topic")
    Group = models.ForeignKey(User_Groups, on_delete=models.CASCADE, blank=True, null=True, related_name="User_Groups")
    Content = models.CharField(max_length=300, default=uuid.uuid1)
    Image = models.ImageField(blank=True, null=True)
    Created = models.DateTimeField(auto_now_add=True)
    Comments = models.ForeignKey('main.Comment', on_delete=models.CASCADE, blank=True, null=True, related_name="comment")
    IsRepost = models.BooleanField(default=False)
    UserHasLiked = models.BooleanField(User, default=False)
    UserHasReposted = models.BooleanField(default=False)
    Likes = models.ManyToManyField(User, blank=True, related_name="likes")
    Reposts = models.ManyToManyField(User, blank=True, related_name="reposts")
    Comment = models.ManyToManyField(User, blank=True, related_name="comments")
    Flags = models.ManyToManyField(User, blank=True, related_name="flags")
    Req_User_Follows_Author = models.BooleanField(default=False)
    slug = models.SlugField(
        default='',
        editable=False,
        max_length=75,
    )
    
    def __str__(self): 
        return self.Content
        

class Repost(models.Model):
    Reposter = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,)
    Post = models.ForeignKey('main.Post', on_delete=models.CASCADE, related_name='reposted')
    Comments = models.ForeignKey('main.RepostComment', on_delete=models.CASCADE, blank=True, null=True, related_name="repost_comment")
    LikeCount = models.PositiveIntegerField(default=0)
    ReshareCount = models.PositiveIntegerField(default=0)
    CommentCount = models.PositiveIntegerField(default=0)
    Created = models.DateTimeField(auto_now_add=True)
    UserHasLiked = models.BooleanField(default=False)
    UserHasReposted = models.BooleanField(default=False)
    slug = models.SlugField(
        default='',
        editable=False,
        max_length=75,
    )
    
    def __str__(self): 
        return self.Post.Content         


class Liked_Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_like")
    liked_post = models.ForeignKey('main.Post', on_delete=models.CASCADE, related_name="posts_liked", blank=True, null=True)
    alreadyLiked = models.BooleanField(default=False)

    def __str__(self):
        return self.liked_post.Content
        
        
class Reshared_Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reshare")
    reshared_post = models.ForeignKey('main.Post', on_delete=models.CASCADE, related_name="posts_reshared", blank=True, null=True)
    alreadyReshared = models.BooleanField(default=False)

    def __str__(self):
        return self.reshared_post.Content
        
        
        
class Commented_Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_commented")
    commented_post = models.ForeignKey('main.Post', on_delete=models.CASCADE, related_name="posts_commented", blank=True, null=True)
    alreadyCommented = models.BooleanField(default=False)

    def __str__(self):
        return self.commented_post.Content         


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users")
    post = models.ForeignKey('main.Post', on_delete=models.CASCADE, related_name="posts", blank=True, null=True)
    alreadyLiked = models.BooleanField(default=False)

    def __str__(self):
        return 'Liked by {} on {}'.format(self.user) 


class Comment(models.Model): 
    post = models.ForeignKey('main.Post', on_delete=models.CASCADE, related_name='comments')
    Author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    body = models.TextField() 
    created = models.DateTimeField(auto_now_add=True) 
    updated = models.DateTimeField(auto_now=True) 

    class Meta: 
        ordering = ('created',) 

    def __str__(self): 
        return self.body
        

class Report(models.Model): 
    Offendor = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    reason = models.TextField() 
    created = models.DateTimeField(auto_now_add=True) 

    class Meta: 
        ordering = ('created',)

        
class Flagged_Post(models.Model):
    post = models.ForeignKey('main.Post', on_delete=models.CASCADE, related_name='flagged')
    created = models.DateTimeField(auto_now_add=True) 

    class Meta: 
        ordering = ('created',)
    
    def __unicode__(self):
       return self.post.Content    



class RepostComment(models.Model): 
    post = models.ForeignKey('main.RePost', on_delete=models.CASCADE, related_name='repost_comments')
    Author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    body = models.TextField() 
    created = models.DateTimeField(auto_now_add=True) 
    updated = models.DateTimeField(auto_now=True) 


    class Meta: 
        ordering = ('created',) 

    def __str__(self): 
        return self.body          
  

class FollowingManager(models.Model):

    def followers(self, user):
        key = cache_key("followers", user.pk)
        followers = cache.get(key)

        if followers is None:
            qs = Follow.objects.filter(followee=user).all()
            followers = [u.follower for u in qs]
            cache.set(key, followers)

        return followers

    def following(self, user):
        key = cache_key("following", user.pk)
        following = cache.get(key)
        

        if following is None:
            qs = Follow.objects.filter(follower=user).all()
            following = [u.followee for u in qs]
            cache.set(key, following)

        return following

    def add_follower(self, follower, followee):
        if follower == followee:
            raise ValidationError("Users cannot follow themselves")

        relation, created = Follow.objects.get_or_create(
            follower=follower, followee=followee
        )

        if created is False:
            raise AlreadyExistsError(
                "User '%s' already follows '%s'" % (follower, followee)
            )

        follower_created.send(sender=self, follower=follower)
        followee_created.send(sender=self, followee=followee)
        following_created.send(sender=self, following=relation)

        bust_cache("followers", followee.pk)
        bust_cache("following", follower.pk)

        return relation

    def remove_follower(self, follower, followee):
        try:
            rel = Follow.objects.get(follower=follower, followee=followee)
            follower_removed.send(sender=self, follower=follower)
            followee_removed.send(sender=self, followee=followee)
            following_removed.send(sender=self, following=rel)
            rel.delete()
            bust_cache("followers", followee.pk)
            bust_cache("following", follower.pk)
            return True
        except Follow.DoesNotExist:
            return False

    def follows(self, follower, followee):
        followers = cache.get(cache_key("following", follower.pk))
        following = cache.get(cache_key("followers", followee.pk))

        if followers and followee in followers:
            return True
        elif following and follower in following:
            return True
        else:
            return Follow.objects.filter(follower=follower, followee=followee).exists()





def _clean_user(user):
    if not app_settings.STAR_RATINGS_ANONYMOUS:
        if not user:
            raise ValueError(_("User is mandatory. Enable 'STAR_RATINGS_ANONYMOUS' for anonymous ratings."))
        return user
    return None
    

class Muted(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="muted")

    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    vehicle_type = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    License_Picture = models.ImageField(blank=True, null=True)
    Profile_Picture = models.ImageField(blank=True, null=True)
    Account_Type = models.ForeignKey(Account_Type, blank=True, null=True, on_delete=models.CASCADE)
    Notifications = models.PositiveIntegerField(default=0)
    Messages = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    
    
class user_pics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    Image = models.ImageField(blank=True, null=True)


class default_profile_pic(models.Model):
      image = models.FileField(blank=True, null=True)
      
      
class Message(models.Model):
      post = models.ForeignKey('main.Post', on_delete=models.CASCADE, related_name='DMsPost', blank=True, null=True)
      sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
      receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
      msg_content = models.TextField(max_length=500, blank=True)
      created_at = models.DateTimeField(auto_now_add=True)     

class Notification(models.Model):
      job = models.ForeignKey('main.Job', on_delete=models.CASCADE, related_name='NotificationJob', blank=True, null=True)
      sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_sender")
      receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_receiver")
      msg = models.TextField(max_length=100, blank=True)
      created_at = models.DateTimeField(auto_now_add=True)
         
