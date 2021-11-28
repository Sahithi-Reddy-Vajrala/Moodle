from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import fields
from .models import Assignment, Courses, Submission,Comment,DirectMessage


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1',
            'password2', 'first_name', 'last_name']


class courseForm(forms.Form):
    course_name = forms.CharField(label='coursename', max_length=255, required=True)
    codeta = forms.CharField(max_length=5,required=True,label="codeta")
    codestudent = forms.CharField(max_length=5,required=True,label="codestudent")

    class Meta:
        model = Courses
        fields = ['course_name']

class joincoursestudentForm(forms.Form):
    code = forms.CharField(max_length=5,required=True,label="codestudent")

class joincoursetaForm(forms.Form):
    code = forms.CharField(max_length=5,required=True,label="codeta")

class UploadAssignmentForm(forms.Form):
    title = forms.CharField(max_length=255)
    uploadfile = forms.FileField(label='Select a file', help_text='max. 42 megabytes')
    totalmarks = forms.IntegerField()
    deadline = forms.DateTimeField(help_text='format:%Y-%m-%d %H:%M')
    weightage = forms.IntegerField()
    
	# class Meta:
	#	model = Assignment
	#	fields = [ 'title', 'uploadfile', 'totalmarks']
	# this works when you only need to save forms and no other modifications on model object.
	
class editForm(forms.Form):
    newfirstname=forms.CharField(max_length=30,label='new_firstname')
    newemail = forms.EmailField(label='new_email')
    newlastname=forms.CharField(max_length=30,label='new_lastname')
    class Meta:
        model = User
        fields = ['newfirstname','newlastname','newemail']

class UploadSubmissionForm(forms.Form):
	ansfile = forms.FileField(label='Select a file',help_text='max. 42 megabytes')

class change_disable(forms.ModelForm):

    class Meta:
        model = Courses
        fields = ['creater_disable']	

class CommentForm(forms.Form):
    comment_body = forms.CharField(max_length=1000)
    class Meta:
        model = Comment
        fields = ['comment_body']


class DM(forms.Form):
    #fromuser = forms.CharField(max_length=30)
    to_user = forms.CharField(max_length=30)
    what_mess = forms.CharField(max_length=1000)

    class Meta:
        model = DirectMessage
        fields = ['to_user','what_mess']