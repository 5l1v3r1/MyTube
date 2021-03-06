from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core import serializers as django_serializers
from video.models import Comment
from .serializers import *
from user_profile.models import UserProfile
from video.models import Video,VideoLike
from user_channel.models import UserChannel
from rest_framework.permissions import IsAuthenticated
import ast
import json
# Create your views here.

class ValidateCredentials(APIView):
	permission_classes = []
	def get(self,request):
		content = {"post_only":True}
		return Response(content)
	def post(self,request):
		username = request.data.get("username")
		password = request.data.get("password")
		user = authenticate(username=username,password=password)
		if user is not None:
			content = {"valid_credentials":True}
		else:
			content = {"valid_credentials":False}
		return Response(content)

class GetCurrentUserProfile(APIView):
	permission_classes = [IsAuthenticated]
	def get(self,request):
		profile = UserProfile.objects.filter(user=request.user)
		json_ = django_serializers.serialize("json",profile)
		return Response(json_)

class FilterComments(APIView):
	permission_classes = []
	def get(self,request,video_id,from_,to_):
		video = Video.objects.filter(pk=video_id)
		if not video:
			return Response({"Video not found with id: {}".format(video_id)})
		comments = Comment.objects.filter(video=video[0]).order_by("-id")
		json_ = django_serializers.serialize("json",comments[from_:to_])
		json_list = ast.literal_eval(json_)
		for comment in json_list:
			user_profile = UserProfile.objects.get(pk=comment["fields"]["user_profile"])
			comment["fields"]["user_profile"] = django_serializers.serialize("json",[user_profile])
		return Response(json.dumps(json_list))

class LikeVideo(APIView):
	permission_classes = [IsAuthenticated]
	def post(self,request):
		type_ = request.data.get("type_")
		response_json = {}
		if type_ not in ["like","dislike"]:
			return Response("[INVALID type_ ( 'like' or 'dislike' )")
		video_id = request.data.get("video_id")
		if not video_id:
			return Response("[MISSING video_id]")
		video = Video.objects.get(pk=video_id)
		current_user = request.user
		userLiked = VideoLike.objects.filter(video=video,user=current_user,like=True,dislike=False)
		userDisliked = VideoLike.objects.filter(video=video,user=current_user,like=False,dislike=True)

		if userLiked and type_ == "like":
			return Response({"created_like":False,"deleted_like":False,"created_dislike":False,"deleted_dislike":False})
		elif userDisliked and type_ == "dislike":
			return Response({"created_like":False,"deleted_like":False,"created_dislike":False,"deleted_dislike":False})

		if not userLiked:
			if type_ == "like":
				if userDisliked:
					userDislike = VideoLike.objects.get(video=video,user=current_user,like=False,dislike=True)
					userDislike.delete()
					response_json["deleted_dislike"] = True
				else:
					response_json["deleted_dislike"] = False
				VideoLike.objects.create(video=video,user=current_user,like=True,dislike=False)
				response_json["created_like"] = True
		elif not userDisliked:
			if type_ == "dislike":
				if userLiked:
					userLike = VideoLike.objects.get(video=video,user=current_user,like=True,dislike=False)
					userLike.delete()
					response_json["deleted_like"] = True
				else:
					response_json["deleted_like"] = False
				VideoLike.objects.create(video=video,user=current_user,like=False,dislike=True)
				response_json["created_dislike"] = True
		return Response(response_json)

class UserChannelsViewSet(viewsets.ModelViewSet):
	queryset = UserChannel.objects.all()
	serializer_class = UserChannelSerializer

class VideosViewSet(viewsets.ModelViewSet):
	queryset = Video.objects.all()
	serializer_class = VideoSerializer
	
class UsersViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer

class UserProfilesViewSet(viewsets.ModelViewSet):
	queryset = UserProfile.objects.all()
	serializer_class = UserProfileSerializer

class CommentsViewSet(viewsets.ModelViewSet):
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer

class CategoriesViewSet(viewsets.ModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer