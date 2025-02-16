from rest_framework import serializers

from .utils import get_or_create_bill
from .models import Tag, Bill, UserBillInteraction, UserKeyword


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class BillSerializer(serializers.ModelSerializer):
    tags = serializers.ListSerializer(child=serializers.CharField(), read_only=True)

    class Meta:
        model = Bill
        fields = "__all__"


class UserBillInteractionSerializer(serializers.ModelSerializer):
    legiscan_bill_id = serializers.IntegerField(
        source="bill.legiscan_bill_id", read_only=True
    )
    bill_number = serializers.CharField(source="bill.bill_number", read_only=True)
    bill_title = serializers.CharField(source="bill.bill_title", read_only=True)

    class Meta:
        model = UserBillInteraction
        fields = [
            "id",
            "legiscan_bill_id",
            "bill_number",
            "bill_title",
            "stance",
            "note",
            "ignore",
        ]


class UserKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserKeyword
        fields = ["id", "keyword"]

    def validate_keyword(self, value):
        """Prevent users from adding duplicate keywords."""
        user = self.context["request"].user
        if UserKeyword.objects.filter(user=user, keyword=value).exists():
            raise serializers.ValidationError("You are already tracking this keyword.")
        return value


# admin-only:


class AdminBillSerializer(serializers.ModelSerializer):
    tags = serializers.ListSerializer(
        child=serializers.CharField(), read_only=True
    )  # Returns tags as a list of names
    tag_names = serializers.ListField(
        write_only=True, child=serializers.CharField(), required=False
    )  # Accepts tag names for updates

    class Meta:
        model = Bill
        fields = [
            "legiscan_bill_id",
            "bill_number",  # Only updated on POST
            "bill_title",  # Only updated on POST
            "tags",  # Readable list of tag names
            "tag_names",  # Used for tag updates
            "admin_stance",
            "admin_note",
            "admin_expanded_analysis_url",
        ]
        read_only_fields = ["legiscan_bill_id", "bill_number", "bill_title"]

    def create(self, validated_data):
        """
        Creates a Bill if it doesn't exist, fetching data from LegiScan externally.
        """

        legiscan_bill_id = self.initial_data.get("legiscan_bill_id")

        if not legiscan_bill_id:
            raise serializers.ValidationError("legiscan_bill_id is required.")

        bill = get_or_create_bill(legiscan_bill_id)

        # Update allowed fields
        tag_names = validated_data.pop("tag_names", [])
        for attr, value in validated_data.items():
            setattr(bill, attr, value)

        # Update tags
        if tag_names:
            import pdb

            pdb.set_trace()
            tag_instances = [
                Tag.objects.get_or_create(name=name)[0] for name in tag_names
            ]
            bill.tags.set(tag_instances)

        bill.save()
        return bill

    def update(self, instance, validated_data):
        """Update admin-related fields and tags."""
        tag_names = validated_data.pop("tag_names", [])

        # Update only allowed fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update tags
        if tag_names:
            tag_instances = [
                Tag.objects.get_or_create(name=name)[0] for name in tag_names
            ]
            instance.tags.set(tag_instances)

        instance.save()
        return instance

    def delete_admin_info(self, instance):
        """Remove admin-related fields but not the bill itself."""
        instance.admin_stance = None
        instance.admin_note = None
        instance.admin_expanded_analysis_url = None
        instance.save()
        return instance
