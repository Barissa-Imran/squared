from rest_framework import serializers
from .models import Item, OrderItem, Order, Address, Transaction, Coupon, Refund
from PIL import Image
from io import BytesIO
from django.core.files import File


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

    def validate(self, data):
        """
        Ensure the discount price is not greater than the actual price
        """
        if data.get('discount_price') and data['discount_price'] >= data['price']:
            raise serializers.ValidationError("Discount price must be less than actual price.")
        return data

    def to_representation(self, instance):
        """
        Modify the output to include a URL for the image.
        """
        representation = super().to_representation(instance)
        if instance.image:
            representation['image'] = instance.image.url
        return representation

    def create(self, validated_data):
        """
        Override the create method to handle image compression.
        """
        image = validated_data.pop('image', None)
        item = Item.objects.create(**validated_data)
        if image:
            item.image = self.compress_image(image)
            item.save()
        return item

    def update(self, instance, validated_data):
        """
        Override the update method to handle image compression.
        """
        image = validated_data.pop('image', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if image:
            instance.image = self.compress_image(image)
        instance.save()
        return instance

    def compress_image(self, image):
        """
        Compress the image before saving.
        """
        img = Image.open(image)
        img_io = BytesIO()
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(img_io, format="JPEG", quality=70, optimize=True)
        new_img = File(img_io, name=image.name)
        return new_img


class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['total_item_price'] = instance.get_total_item_price()
        representation['total_discount_item_price'] = instance.get_total_discount_item_price()
        representation['amount_saved'] = instance.get_amount_saved()
        representation['final_price'] = instance.get_final_price()
        return representation


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['total'] = instance.get_total()
        return representation


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = '__all__'
