from recipes.models import Recipe

data = {
    "ingredients": [{"id": 300, "amount": 3},{"id": 4,"amount": 15}],
    "name": "recipe 4",
    "image": None,
    "text": "rdfgfdgsdfgsdfg",
    "cooking_time": 10,
    "author": 1,
    "tags": [
        2,
        3
        ]
    }
r1 = Recipe.objects.create(**data)