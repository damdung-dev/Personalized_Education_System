# forms.py
from django import forms
from .models import RecommendDocument,ListLesson

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = RecommendDocument
        fields = ['title', 'url','source', 'author']

class VideoForm(forms.ModelForm):
    class Meta:
        model = ListLesson
        fields = ['lesson_name', 'description', 'video_file']

