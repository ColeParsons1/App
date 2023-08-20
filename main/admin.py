from django.contrib import admin
#from tinymce.widgets import TinyMCE
from django.db import models
from django.contrib import admin
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib import auth
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
#from .models import Profile
from API.models import API_Test
from .models import Profile, Job, Topic, Notification, Message, Account_Type, Images, Post, Vid
#from friendship.admin import 
admin.site.register(Job)
admin.site.register(Topic)
#admin.site.register(Images)
#admin.site.register(Post)
admin.site.register(Vid)
admin.site.register(Notification)
admin.site.register(Message)
#admin.site.register(Account_Type)
#admin.site.register(API_Test)




class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'created')
    list_filter = ('created', 'updated')


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'
    fk_name = 'user'


class ModelAdmin(admin.ModelAdmin):
  admin.site.site_header = 'LUG'
  admin.site.site_title = 'Lug'
  class Media:
           
        css = {
             'all': ('main/static/main/admin-extra.css',)
        }
    

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('get_user', 'is_staff', 'get_location','get_birth_date', 'get_profile_pic', )
    list_select_related = ('profile', )
    
    def get_user(self, instance):
        return instance.profile.user.username
    get_user.short_description = 'User'

    def get_birth_date(self, instance):
        return instance.profile.birth_date
    get_birth_date.short_description = 'Birth date'
    
    def get_location(self, instance):
        return instance.profile.location
    get_location.short_description = 'Location'
    
    def get_profile_pic(self, instance):
        return instance.profile.Profile_Picture
    get_profile_pic.short_description = 'Profile Picture'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)
        
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)   
    


