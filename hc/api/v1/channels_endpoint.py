from rest_framework import serializers
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet

from hc.api.models import Channel


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ('code', 'kind', 'value', 'user', 'created', 'checks')


class ChannelsViewSet(ModelViewSet):
    queryset = Channel.objects.all().order_by('-created')
    serializer_class = ChannelSerializer
    search_fields = ('kind', 'user',)
    filter_fields = ('kind', 'user',)


channels_router = DefaultRouter()
channels_router.register(r'channels', ChannelsViewSet)
