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
from .models import User_Groups
from .models import Topic
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from django.core.files import File
import base64


class JobSerializer(serializers.ModelSerializer):
	Job_Type = serializers.SerializerMethodField()
	Assigned_Lugger = serializers.SerializerMethodField()
	Image = serializers.SerializerMethodField()
	def get_Job_Type(self, Job):
		if Job.Job_Type:
			return Job.Job_Type.Label
		return default
	def get_Assigned_Lugger(self, Job):
		if Job.Assigned_Lugger:
			return Job.Assigned_Lugger.username
		else:
			return ""
	def get_Image(self, Job):
		if Job.Image:
			return Job.Image.url
		return ""			
		
	class Meta:
		model = Job
		fields = (
		'id',
		'Business_Name',
		'Job_Type',
		'Load_Weight',
		'Image',
		'ImageString',
		'Pickup_Address',
		'Destination_Address',
		'Tip',
		'Latitude_Pickup',
		'Longitude_Pickup',
		'Latitude_Destination',
		'Longitude_Destination',
		'Distance',
		'Created',
		'InProgress',
		'Complete',
		'Assigned_Lugger',
		)



class ProfileSerializer(serializers.ModelSerializer):
	user = serializers.SerializerMethodField()
	def get_user(self, Profile):
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
		'first_name',
		'last_name',
		'location',
		'birth_date',
		'Account_Type',
		'Profile_Picture',
		'License_Picture',
		)           


class PostSerializer(serializers.ModelSerializer):
    Author = serializers.SerializerMethodField()
    Author_Profile_Picture = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    def get_Author(self, Post):
        if Post.Author.username:
            return Post.Author.username
        return default
    def get_id(self, Post):
        if Post.id:
            return Post.id
        return default
    def get_Author_Profile_Picture(self, Post):
        if Post.Author.Profile.Profile_Picture:
            return Post.Author.Profile.Profile_Picture.url
        return default               
   

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
            'CommentCount',
            'IsRepost',
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

    def to_representation(self, data):
        data = super(PostSerializer, self).to_representation(data)
        data['LikeCount'] = 15
        return data    


class MessageSerializer(serializers.ModelSerializer):
	sender = serializers.SerializerMethodField()
	receiver = serializers.SerializerMethodField()
	def get_sender(self, Message):
		if Message.sender.username:
			return Message.sender.username
		return default
	def get_receiver(self, Message):
		if Message.receiver.username:
			return Message.receiver.username
		return default	
	
		
	class Meta:
		model = Message
		fields = (
		'id',
		'sender',
		'receiver',
		'msg_content',
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
		'created_at',	
		)



class GroupSerializer(serializers.ModelSerializer):
	user = serializers.SerializerMethodField()
	def get_user(self, User_Groups):
		if User_Groups.user.username:
			return User_Groups.user.username
		return default
		
	class Meta:
		model = User_Groups
		fields = (
		'id',
		'user',
		'Label',
		'Members',	
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
            email=validated_data['email'],
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