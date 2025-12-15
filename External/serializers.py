# serializers.py
from rest_framework import serializers
from django.core.files.uploadedfile import UploadedFile, InMemoryUploadedFile
from .models import TicketPanel

class TicketPanelSerializer(serializers.ModelSerializer):
    screenshot_url = serializers.SerializerMethodField() 

    class Meta:
        model = TicketPanel
        fields = [
            'id', 'name', 'department', 'location', 'role', 'imageupload',
            'screenshot_url', 'message', 'paneltype', 'raw_payload', 
            'created_date', 'updated_date'
        ]
        read_only_fields = ['id', 'created_date', 'updated_date', 'raw_payload', 'screenshot_url']

    def get_screenshot_url(self, obj):
        request = self.context.get('request')
        if obj.imageupload and hasattr(obj.imageupload, 'url'):
            return request.build_absolute_uri(obj.imageupload.url)
        return None

    def validate_imageupload(self, value):
        if value and not value.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise serializers.ValidationError("Only PNG/JPG screenshots allowed.")
        return value

    def create(self, validated_data):
       
        request_data = self.context['request'].data
        raw_payload = {}
        for k, v in request_data.items():
            if not isinstance(v, (UploadedFile, InMemoryUploadedFile)):
                raw_payload[k] = v
            else:
                
                raw_payload[k] = {
                    'filename': v.name,
                    'size': v.size,
                    'content_type': v.content_type
                }
        validated_data['raw_payload'] = raw_payload
        
        
        return super().create(validated_data)