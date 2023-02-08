from rest_framework import serializers

from account.models import country, city, state


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = country
        fields = "__all__"


class CountryDetailSerializer(serializers.ModelSerializer):
    cities = serializers.SerializerMethodField()

    def get_cities(self, obj):
        states = state.objects.filter(country=obj).values_list("id")
        cities = city.objects.filter(id__in=states).values("id", "name", "state")
        return cities

    class Meta:
        model = country
        fields = ("name", "id", "cities")


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = city
        fields = "__all__"
