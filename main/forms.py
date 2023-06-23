from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import HiddenInput
from .models import Post
from .models import Comment
from .models import Profile
from .models import Report, Message, user_pics, Topic, Job
#from friendship.models import Follow, Block
#from .models import FollowingManager
import ast
import json
from geopy.geocoders import Nominatim
import geopy.distance
from geopy.adapters import AioHTTPAdapter
import requests
import urllib.parse
#from .models import UserRating
#from django.db.models.loading import get_model

#Libro = get_model('Post')


class MyForm (forms.Form):
    def __init__ (self, Topic, Content, *args, **kwargs):
        self.Content = Topic
        self.desc = Content
        super (MyForm, self).__init__ (*args, **kwargs)



class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('body',)
        

class ReportForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ('reason',)

        
class MessageForm(forms.ModelForm):
    receiver = forms.ModelChoiceField(label="Send to:",queryset=User.objects.order_by('username'))
    msg_content = forms.CharField(label='Text', max_length=100, required=False)
    #post = forms.ModelChoiceField(queryset=Post.objects.order_by('Created').reverse())

    class Meta:
        model = Message
        fields = ('receiver', 'msg_content',)
        
    #def __init__(self, *args, **kwargs):
        #super(MessageForm, self).__init__(*args, **kwargs)
        #self.fields['post'].required = False     
        
        
class DMPostForm(forms.ModelForm):
    receiver = forms.ModelChoiceField(queryset=User.objects.order_by('username'))

    class Meta:
        model = Message
        fields = ('receiver',)          


YEARS = [x for x in range(1940,2021)]    
class ProfileForm(forms.ModelForm):
    birth_date = forms.DateField(label="When's your birthday?", widget=forms.SelectDateWidget(years=YEARS))
    location = forms.CharField(label='Location',max_length=30, required=False)
    profile_pic = forms.ImageField(widget = forms.FileInput())

    class Meta:
        model = User
        fields = ('birth_date', 'location', 'profile_pic', )
        
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['profile_pic'].required = False
        
        
class ImageForm(forms.ModelForm):
    Image = forms.ImageField(widget = forms.FileInput())

    class Meta:
        model = user_pics
        fields = ('Image', )
        
    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)
        self.fields['Image'].required = False          
        

YEARS = [x for x in range(1940,2021)]        
class Profile(forms.ModelForm):

    birth_date = forms.DateField(label="Birth date", widget=forms.SelectDateWidget(years=YEARS))

    class Meta:
        model = Profile
        fields = ('birth_date', 'location', 'Profile_Picture',)        

my_default_errors = {
    'invalid': 'Vibe Check'
}

class PostForm(forms.ModelForm):

    Content = forms.CharField(label='Text', widget=forms.TextInput(attrs={'rows':4, 'cols':15}), error_messages=my_default_errors)
    Image = forms.ImageField(widget = forms.FileInput())
    Topic = forms.ModelChoiceField(queryset=Topic.objects.order_by('Label'))

    class Meta:
        model = Post
        fields = ('Topic', 'Image', 'Content',)
        
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['Image'].required = False
        self.fields['Content'].required = False 
        self.fields['Topic'].required = False

    def clean_Content(self):
        Content = self.cleaned_data.get('Content')
        
        if Content:
            if "politics" not in Content: 
                Content = Content
            else:
                Content = "My vibe has been checked :("
                
        return Content 

Invalid = "politics, political"        
class JobForm(forms.ModelForm):

    Business_Name = forms.CharField(label='Business Name', widget=forms.TextInput(attrs={'rows':4, 'cols':15}), error_messages=my_default_errors)
    Pickup_Address = forms.CharField(label='Pickup_Address', widget=forms.TextInput(attrs={'rows':1, 'cols':15}), error_messages=my_default_errors)
    Destination_Address = forms.CharField(label='Destination_Address', widget=forms.TextInput(attrs={'rows':1, 'cols':15}), error_messages=my_default_errors)
    Job_Type = forms.ModelChoiceField(queryset=Topic.objects.order_by('Label'))
    Load_Weight = forms.IntegerField(label='Weight', required=False)
    Latitude_Pickup = forms.HiddenInput()
    Longitude_Pickup = forms.HiddenInput()
    Latitude_Destination = forms.HiddenInput()
    Longitude_Destination = forms.HiddenInput()
    Distance = forms.HiddenInput()


    class Meta:
        model = Job
        fields = ('Business_Name', 'Pickup_Address', 'Destination_Address', 'Job_Type', 'Load_Weight', 'Latitude_Pickup','Longitude_Pickup','Latitude_Destination','Longitude_Destination','Distance')
        
    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        self.fields['Latitude_Pickup'].required = False
        self.fields['Longitude_Pickup'].required = False
        self.fields['Latitude_Destination'].required = False
        self.fields['Longitude_Destination'].required = False
        self.fields['Distance'].required = False

    def clean_Pickup_Address(self):
        Pickup_Address = self.cleaned_data.get('Pickup_Address')
             
        return Pickup_Address

    def clean_Destination_Address(self):
        Destination_Address = self.cleaned_data.get('Destination_Address')
             
        return Destination_Address    
        
    def clean_Latitude_Pickup(self):
        
        self.Pickup_Address = self.data.get('Pickup_Address')
        #geolocator = Nominatim(user_agent="mysite2")
        #location = geolocator.geocode(self.Pickup_Address)
        #self.Latitude_Pickup = location.latitude
        #self.Longitude_Pickup = location.longitude
        response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+urllib.parse.quote(self.Pickup_Address)+'&key=AIzaSyBCTEHjteAUobF6e3tqcMnkZC-2cGBQSkU')

        resp_json_payload = response.json()

        print(resp_json_payload['results'][0]['geometry']['location']['lat'])
        self.Latitude_Pickup = resp_json_payload['results'][0]['geometry']['location']['lat']
        #url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(self.Pickup_Address) +'?format=json'

        #response = requests.get(url).json()

             
        return self.Latitude_Pickup

    def clean_Longitude_Pickup(self):
        self.Pickup_Address = self.data.get('Pickup_Address')
        #geolocator = Nominatim(user_agent="mysite2")
        #location = geolocator.geocode(self.Pickup_Address)
        #self.Latitude_Pickup = location.latitude
        #self.Longitude_Pickup = location.longitude

        response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+urllib.parse.quote(self.Pickup_Address)+'&key=AIzaSyBCTEHjteAUobF6e3tqcMnkZC-2cGBQSkU')

        resp_json_payload = response.json()

        print(resp_json_payload['results'][0]['geometry']['location']['lng'])
        self.Longitude_Pickup = resp_json_payload['results'][0]['geometry']['location']['lng']
             
        return self.Longitude_Pickup

    def clean_Latitude_Destination(self):
        self.Destination_Address = self.data.get('Destination_Address')
        response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+urllib.parse.quote(self.Destination_Address)+'&key=AIzaSyBCTEHjteAUobF6e3tqcMnkZC-2cGBQSkU')
        resp_json_payload = response.json()
        print(resp_json_payload['results'][0]['geometry']['location']['lat'])
        self.Latitude_Destination = resp_json_payload['results'][0]['geometry']['location']['lat']
        return self.Latitude_Destination

    def clean_Longitude_Destination(self):
        self.Destination_Address = self.data.get('Destination_Address')
        response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+urllib.parse.quote(self.Destination_Address)+'&key=AIzaSyBCTEHjteAUobF6e3tqcMnkZC-2cGBQSkU')
        resp_json_payload = response.json()
        print(resp_json_payload['results'][0]['geometry']['location']['lng'])
        self.Longitude_Destination = resp_json_payload['results'][0]['geometry']['location']['lng'] 
        return self.Longitude_Destination

    def clean_Distance(self):
        coords_1 = (self.Latitude_Pickup, self.Longitude_Pickup)
        coords_2 = (self.Latitude_Destination, self.Longitude_Destination)
        self.Distance = geopy.distance.geodesic(coords_1, coords_2).miles  
        return self.Distance   


        
YEARS = [x for x in range(1940,2021)]
class sign(UserCreationForm):
    email = forms.EmailField(label='Email',max_length=54, required=True, help_text='')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    birth_date = forms.DateField(label="When's your birthday?", widget=forms.SelectDateWidget(years=YEARS))
    bio = forms.CharField(label='Bio',widget=forms.Textarea, max_length=260, required=False)
    location = forms.CharField(label='Location',max_length=30, required=False)
    profile_pic = forms.FileField(label='Profile Picture',required=False)
    class Meta:
        model = User
        fields = ('username', 'birth_date', 'location', 'bio', 'profile_pic',)

        
YEARS = [x for x in range(1940,2021)]        
class user_edit_profile(forms.ModelForm):
    
    birth_date = forms.DateField(label="When's your birthday?", widget=forms.SelectDateWidget(years=YEARS))
    bio = forms.CharField(label='Bio',widget=forms.Textarea, max_length=260, required=False)
    location = forms.CharField(label='Location',max_length=30, required=False)
    profile_pic = forms.FileField(label='Profile Picture',required=False)

    class Meta:
        model = User
        fields = ('username', 'birth_date', 'location', 'bio', 'profile_pic',)  


class report(forms.ModelForm):
    message = forms.CharField(label='Location',max_length=30, required=False)
    #'email','password1', 'password2',
    class Meta:
        model = User
        fields = ('message',)


class ImageForm(forms.ModelForm):
    Image = forms.ImageField(widget = forms.FileInput())

    class Meta:
        model = user_pics
        fields = ('Image', )
        
    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)
        self.fields['Image'].required = False          

        
