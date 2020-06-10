from rest_framework import serializers
from wt.att_subscriptions.models import ATTSubscription


class ATTSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ATTSubscription
        fields = "__all__"


class UsageRecordSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=25, required=False)
    exceeded_limit = serializers.FloatField(required=False)


class ATTSubscriptionPriceLimitSerializer(serializers.Serializer):
    subscription_id = serializers.IntegerField()
    usage_record = serializers.ListField(UsageRecordSerializer())


class ATTSubscriptionFilterPriceLimitSerializer(serializers.Serializer):
    l_min = serializers.FloatField(required=False)
    l_max = serializers.FloatField()


class ATTSubscriptionDateFilterSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=25)
    from_d = serializers.DateTimeField(required=True)
    to_d = serializers.DateTimeField(required=True)


class ATTSubscriptionOtherSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=25)
    total_usage = serializers.FloatField()


class ATTSubscriptionDateSerializer(serializers.Serializer):
    subscription_id = serializers.IntegerField(read_only=True)
    type = serializers.CharField(max_length=25)
    total_usage = serializers.FloatField()
    other_sub = serializers.ListField(ATTSubscriptionOtherSerializer())
