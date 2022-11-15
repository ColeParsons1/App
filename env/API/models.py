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
#from star_ratings import app_settings, get_star_ratings_rating_model_name, get_star_ratings_rating_model

import uuid


       
class API_Test(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    Label = models.CharField(max_length=50)
    Members = models.ManyToManyField(User, blank=True, related_name="memberssAPI")
    
    def __unicode__(self):
       return self.Label     
 




        

   
