from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import Profile
from .models import Post
from .models import Account_Type
from .models import Job
from .models import Topic
from .models import Message
from .models import Notification
from .models import Topic, Images, Vid
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from django.core.files import File
import base64
import requests
import urllib
from typing import Any, Dict
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer, Serializer
#from .models import CustomUser
from rest_framework.fields import CharField,ListField
from rest_framework.serializers import ModelSerializer
from API.models import Event

class EventSerializer(ModelSerializer[Event]):
    attendee = ListField(child=CharField(required=False), required=False)

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'start_at', 'end_at', 'location', 'attendee',)
        extra_kwargs = {'attendee': {'required': False, "allow_null": True}}



def clean_string_capitalize(value: str) -> str:
    """Clean string and capitalize it."""
    return value.strip().lower().capitalize()



class StripeSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Vid
		fields = (
		'id',
		'Video',
		)


class VideoSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Vid
		fields = (
		'id',
		'Video',
		)

class TemplateSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Images
		fields = (
		'id',
		'Image',
		)


class JobSerializer(serializers.ModelSerializer):
	Job_Type = serializers.SerializerMethodField()
	Author = serializers.SerializerMethodField()
	Assigned_Lugger = serializers.SerializerMethodField()
	Image = serializers.SerializerMethodField()
	CompletionImage = serializers.SerializerMethodField()
	def get_Job_Type(self, Job):
		if Job.Job_Type:
			return Job.Job_Type.Label
		return default
	def get_Author(self, Job):
		if Job.Author:
			return Job.Author.username
		else:
			return "None"
	def get_Assigned_Lugger(self, Job):
		if Job.Assigned_Lugger:
			return Job.Assigned_Lugger.username
		else:
			return "None"
	def get_Image(self, Job):
		if Job.Image:
			return Job.Image.url
		return ""
	def get_CompletionImage(self, Job):
		if Job.CompletionImage:
			return Job.CompletionImage.url
		return ""

		
	class Meta:
		model = Job
		fields = (
		'id',
		'Author',
		'Business_Name',
		'Job_Type',
		'Description',
		'Load_Weight',
		'Length',
		'Width',
		'Height',
		'Pieces',
		'ImageString',
		'Image',
		'CompletionImage',
		'Pickup_Address',
		'Destination_Address',
		'Time_Needed',
		'Tip',
		'Phone_Number',
		'Price',
		'Latitude_Pickup',
		'Longitude_Pickup',
		'Latitude_Destination',
		'Longitude_Destination',
		'Distance',
		'Created',
		'InProgress',
		'Complete',
		'Driver_Pay',
		'Assigned_Lugger',
		)



class ProfileSerializer(serializers.ModelSerializer):
	user = serializers.SerializerMethodField()
	username = serializers.SerializerMethodField()
	def get_user(self, Profile):
		if Profile.user.username:
			return Profile.user.username
		return default
	def get_username(self, Profile):
		if Profile.user.username:
			return Profile.user.username
		return default	
	def get_Profile_Picture(self, Profile):
		if Profile.Profile_Picture:
			return Profile.Profile_Picture.url
		return default

	
	class Meta:
		model = Profile
		fields = (
		'id',	
		'user',
		'username',
		'first_name',
		'last_name',
		'location',
		'birth_date',
		'Account_Type',
		'Balance',
		'Profile_Picture',
		'License_Picture',
		'License_Plate_Number',
		'Bank_Name',
		'Banking_Account_Number',
		'Banking_Routing_Number',
		'Notifications',
		'Stripe_Link',
		'Stripe_Customer_ID',
		'Stripe_Account_ID',
		'lat',
		'lon',
		'Token',
		)           


class PostSerializer(serializers.ModelSerializer):
	Author = serializers.SerializerMethodField()
	Author_Profile_Picture = serializers.SerializerMethodField()
	Image = serializers.SerializerMethodField()
	Image2 = serializers.SerializerMethodField()
	Image3 = serializers.SerializerMethodField()
	Image4 = serializers.SerializerMethodField()
	RepostAuthor = serializers.SerializerMethodField()
	def get_Author(self, Post):
		if Post.Author:
			return Post.Author.username
		return ""
	def get_Author_Profile_Picture(self, Post):
		if Post.Author.profile.Profile_Picture:
			return Post.Author.profile.Profile_Picture.url
		return ""
	def get_Image(self, Post):
		if Post.Image:
			return Post.Image.url
		return ""
	def get_Image2(self, Post):
		if Post.Image2:
			return ""
		return ""
	def get_Image3(self, Post):
		if Post.Image3:
			return ""
		return ""
	def get_Image4(self, Post):
		if Post.Image4:
			return ""
		return ""			
	def get_RepostAuthor(self, Post):
		if Post.RepostAuthor:
			return Post.RepostAuthor.profile.Display_Name
		return ""	                                 
   

	class Meta:
		model = Post
		fields = (
			'id',
			'Topic',
			'Author',
			'Author_Profile',
			'Author_Profile_Picture',
			'Content',
			'LikeCount',
			'ReshareCount',
			'Image',
			'Image2',
			'Image3',
			'Image4',
			'ImageString',
			'CommentCount',
			'IsRepost',
			'IsLike',
			'IsComment',
			'UserHasLiked',
			'UserHasReposted',
			'Reposted',
			'RepostAuthor',
			'Likes',
			'Reposts',
			'Comment',
			'Flags',
			'Created',
			'Req_User_Follows_Author',
		) 


class MessageSerializer(serializers.ModelSerializer):
	sender = serializers.SerializerMethodField()
	receiver = serializers.SerializerMethodField()
	Image = serializers.SerializerMethodField()
	job = serializers.SerializerMethodField()
	def get_sender(self, Message):
		if Message.sender.username:
			return Message.sender.username
		return default
	def get_receiver(self, Message):
		if Message.receiver.username:
			return Message.receiver.username
		return default
	def get_Image(self, Job):
		if Job.Image:
			return Job.Image.url
		return ""
	def get_job(self, Message):
		if Message.job:
			return Message.job.id
		return default	
	
		
	class Meta:
		model = Message
		fields = (
		'id',
		'job',
		'sender',
		'receiver',
		'msg_content',
		'Image',
		'ImageString',
		'created_at',	
		)


class NotificationSerializer(serializers.ModelSerializer):
	job = serializers.SerializerMethodField()
	sender = serializers.SerializerMethodField()
	receiver = serializers.SerializerMethodField()
	def get_receiver(self, Notification):
		if Notification.receiver.username:
			return Notification.receiver.username
		return default
	def get_sender(self, Notification):
		if Notification.sender.username:
			return Notification.sender.username
		return default
	def get_job(self, Notification):
		if Notification.job:
			return Notification.job.id
		return default		

		
	class Meta:
		model = Notification
		fields = (
		'id',
		'job',
		'sender',
		'receiver',
		'msg',
		'isPickedUpNotification',
		'isInProgressNotification',
		'isMessageNotification',
		'isCompleteNotification',
		'created_at',	
		)


class TopicSerializer(serializers.ModelSerializer):
		
	class Meta:
		model = Topic
		fields = (
		'id',
		'Label',	
		)

class LogoutSerializer(serializers.Serializer):
	class Meta:
		model = User
		username = serializers.CharField(max_length=255)
		password = serializers.CharField(max_length=128, write_only=True)

	def validate(self, data):
		username = data.get('username')
		password = data.get('password')
		if username and password:

			user = authenticate(request=self.context.get('request'),
								username=username, password=password)
			if user:
				data['user'] = user

			data['user'] = user
		return data

class LoginSerializer(serializers.Serializer):
	class Meta:
		model = User
		username = serializers.CharField(max_length=255)
		password = serializers.CharField(max_length=128, write_only=True)

	def validate(self, data):
		username = data.get('username')
		password = data.get('password')
		if username and password:

			user = authenticate(request=self.context.get('request'),
								username=username, password=password)
			if user:
				data['user'] = user

			data['user'] = user
		return data

class SignupSerializer(serializers.Serializer):
	class Meta:
		model = User
		username = serializers.CharField(max_length=255)
		email = serializers.CharField(max_length=255)
		password = serializers.CharField(max_length=128, write_only=True)

	def validate(self, data):
		username = data.get('username')
		password = data.get('password')
		if username and password:

			user = authenticate(request=self.context.get('request'),
								username=username, password=password)
			if user:
				data['user'] = user

			data['user'] = user
		return data


class RegisterSerializer(serializers.Serializer):
	email = serializers.EmailField(
			required=True,
			validators=[UniqueValidator(queryset=User.objects.all())]
			)

	password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
	password2 = serializers.CharField(write_only=True, required=True)
	username = email
	#Account_Type = serializers.ModelField(write_only=True, required=True, queryset=Account_Type.objects.all())


	class Meta:
		model = User
		fields = ('username', 'password', 'password2', 'email',)

	def validate(self, attrs):
		if attrs['password'] != attrs['password2']:
			raise serializers.ValidationError({"password": "Password fields didn't match."})

		return attrs

	def create(self, validated_data):
		user = User.objects.create(
			username=validated_data['username'],
			email=validated_data['username'],
		)

		
		user.set_password(validated_data['password'])
		user.save()
		

		return user

		




#def get_Image(self, Post):
		#f = open(Post.Author.Profile.Profile_Picture, 'rb')
		#image = File(f)
		#data = base64.b64encode(image.read())
		#f.close()
		#return data				        