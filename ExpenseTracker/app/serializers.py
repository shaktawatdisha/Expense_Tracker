from rest_framework import serializers
from .models import Expense, Category
from datetime import datetime

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ExpenseSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_name = serializers.CharField(source='category.name', read_only=True)
    date = serializers.DateField(format="%d %B %Y", read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'user', 'category', 'category_name', 'amount', 'description', 'date']
        read_only_fields = ['user'] 

    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['date'] = datetime.date.today()
        return super().create(validated_data)
