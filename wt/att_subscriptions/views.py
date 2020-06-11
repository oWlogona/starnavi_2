from django.db.models import Sum
from django.http import Http404
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from wt.att_subscriptions.models import ATTSubscription
from wt.att_subscriptions.serializers import ATTSubscriptionSerializer, ATTSubscriptionFilterPriceLimitSerializer, \
    ATTSubscriptionPriceLimitSerializer, ATTSubscriptionDateFilterSerializer, ATTSubscriptionDateSerializer
from wt.usage.models import DataUsageRecord, VoiceUsageRecord


class ATTSubscriptionViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.
    """
    queryset = ATTSubscription.objects.all()
    serializer_class = ATTSubscriptionSerializer


class ATTSubscriptionDetail(APIView):

    @staticmethod
    def get_object(pk):
        try:
            return ATTSubscription.objects.get(pk=pk)
        except ATTSubscription.DoesNotExist:
            raise Http404

    @staticmethod
    def get_date_record_by_id(t_instance, date_from, date_to, pk):
        try:
            return t_instance.objects.select_related('att_subscription_id').filter(
                att_subscription_id=pk,
                att_subscription_id__effective_date__gt=date_from,
                att_subscription_id__effective_date__lt=date_to
            )
        except t_instance.DoesNotExist:
            raise Http404

    @staticmethod
    def get_date_record(t_instance, date_from, date_to, pk):
        try:
            return t_instance.objects.select_related('att_subscription_id').filter(
                att_subscription_id__effective_date__gt=date_from,
                att_subscription_id__effective_date__lt=date_to
            ).exclude(att_subscription_id=pk)
        except t_instance.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        att_sub_obj = self.get_object(pk)
        serializer = ATTSubscriptionSerializer(att_sub_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        serializer_filter = ATTSubscriptionDateFilterSerializer(data=request.data)
        if not serializer_filter.is_valid():
            return Response(serializer_filter.errors, status=status.HTTP_400_BAD_REQUEST)
        date_from = serializer_filter.data.get('from_d')
        date_to = serializer_filter.data.get('to_d')
        record_type = serializer_filter.data.get('type')
        if record_type == 'voice_record':
            data_record_query = self.get_date_record_by_id(VoiceUsageRecord, date_from, date_to, pk)
            sum_record_price = data_record_query.aggregate(Sum('price'))
        elif record_type == 'data_record':
            data_record_query = self.get_date_record_by_id(DataUsageRecord, date_from, date_to, pk)
            sum_record_price = data_record_query.aggregate(Sum('price'))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data_usage = self.get_date_record(DataUsageRecord, date_from, date_to, pk)
        sum_data_usage = data_usage.aggregate(Sum('price'))
        voice_usage = self.get_date_record(VoiceUsageRecord, date_from, date_to, pk)
        sum_voice_usage = voice_usage.aggregate(Sum('price'))

        data = [{'subscription_id': pk, 'type': record_type,
                 'total_usage': float(sum_record_price.get('price__sum') if sum_record_price.get('price__sum') else 0),
                 'other_sub': [
                     {'type': 'DataUsageRecord', 'total_usage': float(
                         sum_data_usage.get('price__sum') if sum_data_usage.get('price__sum') else 0)},
                     {'type': 'VoiceUsageRecord', 'total_usage': float(
                         sum_voice_usage.get('price__sum') if sum_voice_usage.get('price__sum') else 0)}
                 ]}]
        serializer_data = ATTSubscriptionDateSerializer(data, many=True)
        return Response(serializer_data.data, status=status.HTTP_200_OK)


class ATTSubscriptionPriceLimit(APIView):

    @staticmethod
    def data_limit_price(data_record, data_type, limit_price) -> dict:
        obj_dict = {}
        for item in data_record:
            obj_dict[item.id] = {'type': data_type, 'exceeded_limit': float(item.price) - limit_price}
        return obj_dict

    @staticmethod
    def data_union_dict(data_record, voice_record) -> list:
        data = []
        same_subscription_id = set(data_record.keys()).intersection(set(voice_record.keys()))
        for key in same_subscription_id:
            data.append({'subscription_id': key, 'usage_record': [data_record.pop(key), voice_record.pop(key)]})
        for key in data_record.keys():
            data.append({'subscription_id': key, 'usage_record': [data_record.get(key)]})
        for key in voice_record.keys():
            data.append({'subscription_id': key, 'usage_record': [voice_record.get(key)]})
        return data

    @staticmethod
    def get_record(t_instance, limit_price):
        try:
            return t_instance.objects.select_related('att_subscription_id').filter(price__gt=limit_price)
        except t_instance.DoesNotExist:
            raise Http404

    def post(self, request):
        limit_serializer = ATTSubscriptionFilterPriceLimitSerializer(data=request.data)
        if not limit_serializer.is_valid():
            return Response(limit_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data_obj_record = self.get_record(DataUsageRecord, limit_serializer.data.get('l_max'))
        voice_obj_record = self.get_record(VoiceUsageRecord, limit_serializer.data.get('l_max'))
        data_obj_record = self.data_limit_price(data_obj_record, 'DataUsageRecord',
                                                limit_serializer.data.get('l_max')) if data_obj_record else {}
        voice_obj_record = self.data_limit_price(voice_obj_record, 'VoiceUsageRecord',
                                                 limit_serializer.data.get('l_max')) if voice_obj_record else {}
        data = self.data_union_dict(data_obj_record, voice_obj_record)
        serializer = ATTSubscriptionPriceLimitSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
