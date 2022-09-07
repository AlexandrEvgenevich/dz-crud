from rest_framework import serializers
from .models import Product, Stock, StockProduct


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title', 'description']

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance

    def destroy(self, validated_data):
        return super().destroy(validated_data)


class ProductPositionSerializer(serializers.ModelSerializer):
    # настройте сериализатор для позиции продукта на складе
    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['address', 'products', 'positions']

    def create(self, validated_data):

        positions = validated_data.pop('positions')

        stock = super().create(validated_data)

        stock_objects = Stock.objects.all()
        stock_id = [s.id for s in stock_objects if s.address == validated_data['address']]

        for p in positions:
            StockProduct.objects.create(
                stock=Stock.objects.get(id=int(stock_id[0])),
                product=p['product'],
                quantity=p['quantity'],
                price=p['price'])

        return stock

    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц

        stpro_filt = StockProduct.objects.filter(stock=instance.id)
        positions = validated_data.pop('positions')

        # обновляем склад по его параметрам
        stock = super().update(instance, validated_data)

        stpro_list = []

        for s in stpro_filt:
            stpro_list.append(s.product)

        for list_pos in positions:
            if list_pos['product'] in stpro_list:
                for stpro in stpro_filt:
                    for p in positions:
                        if stpro.product == p['product']:
                            stpro.price = p['price']
                            stpro.quantity = p['quantity']
                            stpro.save()
            else:
                for p in positions:
                    if p['product'] not in stpro_list:
                        StockProduct.objects.create(
                            stock=stpro_filt[0].stock,
                            product=p['product'],
                            quantity=p['quantity'],
                            price=p['price'])


        # for s in stpro_filt:
        #     for p in positions:
        #         if s.product == p['product']:
        #             s.price = p['price']
        #             s.quantity = p['quantity']
        #             s.save()
        #             is_product = True


        # здесь вам надо обновить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions

        return stock

    def destroy(self, validated_data):
        return super().destroy(validated_data)
