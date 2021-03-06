from django.db import models
from user_channel.models import UserChannel
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from user_profile.models import UserProfile
import mimetypes

def get_extensions_for_type(general_type):
    for ext in mimetypes.types_map:
        if mimetypes.types_map[ext].split('/')[0] == general_type:
            yield ext[1:]


VIDEO = tuple(get_extensions_for_type('video'))

class Category(models.Model):
	name = models.CharField(max_length=100)
	def __str__(self):
		return f"{self.id} - {self.name}"

class Video(models.Model):
	channel = models.ForeignKey(UserChannel,on_delete=models.CASCADE)
	category = models.ForeignKey(Category,on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	video_file = models.FileField(upload_to="videos",
		validators=[FileExtensionValidator(allowed_extensions=VIDEO)])
	thumbnail = models.ImageField(upload_to="thumbnails")
	title = models.CharField(max_length=300)
	description = models.TextField()

class VideoLike(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	video = models.ForeignKey(Video,on_delete=models.CASCADE)
	like = models.BooleanField()
	dislike = models.BooleanField()

class Comment(models.Model):
	user_profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	video = models.ForeignKey(Video,on_delete=models.CASCADE)
	content = models.TextField()

	def __str__(self):
		if len(self.content) < 300:
			return self.content
		else:
			return self.content[300:] + "..."

class CommentLike(models.Model):
	user_profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	comment = models.ForeignKey(Comment,on_delete=models.CASCADE)
	like = models.BooleanField()
	dislike = models.BooleanField()

class UserView(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	browser = models.TextField()
	video = models.ForeignKey(Video,on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True)
	

class AnonymousView(models.Model):
	browser = models.TextField()
	video = models.ForeignKey(Video,on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True)

