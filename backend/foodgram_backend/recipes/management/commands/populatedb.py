from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from recipes.models import Tag, Ingredient, Recipe, IngredientInRecipe

User = get_user_model()

class Command(BaseCommand):
    def handle(self, *args, **options):
        user1 = User.objects.create(username='user_1',
                     email='user_1@mail.testmail')
        user1.set_password('password')

        user2 = User.objects.create(username='user_2',
                     email='user_2@mail.testmail')
        user2.set_password('password')

        user3 = User.objects.create(username='user_3',
                     email='user_3@email.testmail')
        user3.set_password('password')

        breakfast_tag = Tag.objects.create(name='завтрак', color='#9911AA', slug='breakfast')
        dinner_tag = Tag.objects.create(name='обед', color='#ffaa11', slug='dinner')
        drink_tag = Tag.objects.create(name='напиток', color='#11ffaa', slug='drink')
        porridge_tag = Tag.objects.create(name='каша', color='#113355', slug='porridge')
        desert_tag = Tag.objects.create(name='десерт', color='#bb3355', slug='desert')

        kompot = Recipe.objects.create(
            name = 'компот',
            author=user1,
            image='recipes/images/смородина.jpg',
            text='промойте ягоды, положите в кастрюлю с холодной водой и доведите до кипения. Сразу после закипания снимите кастрюлю с огня',
            cooking_time=10
        )
        water = Ingredient.objects.get(name='вода')
        redcurrant = Ingredient.objects.get(name='красная смородина')
        IngredientInRecipe.objects.create(recipe=kompot, ingredient=water, amount = 500)
        IngredientInRecipe.objects.create(recipe=kompot, ingredient=redcurrant, amount=100)
        kompot.tags.add(drink_tag, desert_tag)

        shashlik = Recipe.objects.create(
            name = 'шашлык из свинины',
            author=user1,
            image='recipes/images/шашлык.jpg',
            text='купите мясо, замаринуйте его как-нибудь по вкусу и жарьте. Пригласите друзей и вообще.',
            cooking_time=90
        )
        meat = Ingredient.objects.get(name='свинина')
        onion = Ingredient.objects.get(name='лук белый')
        vinegar = Ingredient.objects.get(name='уксус 9%')
        IngredientInRecipe.objects.create(recipe=shashlik, ingredient=meat, amount=1500)
        IngredientInRecipe.objects.create(recipe=shashlik, ingredient=onion, amount=300)
        IngredientInRecipe.objects.create(recipe=shashlik, ingredient=vinegar, amount=20)
        shashlik.tags.add(dinner_tag)

        lemontea = Recipe.objects.create(
            name = 'чай с лимоном',
            author=user1,
            image='recipes/images/чай.jpg',
            text='Положите дольку лимона в чай. Через минуту добавьте сахар. Не забудьте перемешать.',
            cooking_time=5
        )
        tea = Ingredient.objects.get(name='чай эрл грей')
        lemon = Ingredient.objects.get(name='лимоны')
        shugar = Ingredient.objects.get(name='сахар')
        IngredientInRecipe.objects.create(recipe=lemontea, ingredient=tea, amount=1)
        IngredientInRecipe.objects.create(recipe=lemontea, ingredient=lemon, amount=20)
        IngredientInRecipe.objects.create(recipe=lemontea, ingredient=shugar, amount=10)
        lemontea.tags.add(drink_tag)

        dumplings_ordinar = Recipe.objects.create(
            name = 'пельмени',
            author=user2,
            image='recipes/images/пельмени.jpg',
            text='Купите в магазине пельмени, положете  кипящую воду. Вскоре утопленники всплывут вверх брюхом. Спустя 10 минут их можно вылавливать и есть. Не обожгитесь.',
            cooking_time=25
        )
        dumplings = Ingredient.objects.get(name='пельмени')
        IngredientInRecipe.objects.create(recipe=dumplings_ordinar, ingredient=dumplings, amount=800)
        IngredientInRecipe.objects.create(recipe=dumplings_ordinar, ingredient=water, amount = 2000)
        dumplings_ordinar.tags.add(dinner_tag)

        dumplings_fried = Recipe.objects.create(
            name = 'пельмени жареные',
            author=user2,
            image='recipes/images/пельмени жареные.jpg',
            text='Возьмите из холодильника вареные пельмени, которые вы ен доели вчера. Положите на разогретую сковороду, смазанную маслом. Жарьте до образования хрустящей корочки, положите в тарелку и хрустите. бон апети',
            cooking_time=25
        )
        IngredientInRecipe.objects.create(recipe=dumplings_fried, ingredient=dumplings, amount=800)
        dumplings_fried.tags.add(dinner_tag, breakfast_tag)

        fried_eggs = Recipe.objects.create(
            name = 'яичница глазунья',
            author=user2,
            image='recipes/images/яичница.jpg',
            text='Два яйца аккуратно разбейте и вылейте содержимое на разогретую сковороду. Масло не забудьтеперед этим налить, а то все прилипнет. Жарьте не накрывая крышкой. ',
            cooking_time=12
        )
        eggs = Ingredient.objects.get(name='яйца куриные')
        IngredientInRecipe.objects.create(recipe=fried_eggs, ingredient=eggs, amount=150)
        fried_eggs.tags.add(breakfast_tag)

        boiled_eggs = Recipe.objects.create(
            name = 'вареное яйцо',
            author=user2,
            image='recipes/images/яйцо вареное.jpg',
            text='Положите яйцов холодную воду и поставте на огонь. После закипания подождете 5 минут и снимайте с огня. Обязательно почистите яцо перед употреблением в пищу. Чтобы легче чистилось лучше сразу по готовности залить яйцо холодной водой и остудить там.',
            cooking_time=10
        )
        IngredientInRecipe.objects.create(recipe=boiled_eggs, ingredient=eggs, amount=75)
        boiled_eggs.tags.add(breakfast_tag)

        poached_egg = Recipe.objects.create(
            name = 'яйцо пашот',
            author=user2,
            image='recipes/images/яйцо пашот.jpg',
            text='Разбейте яйцо в половник не повредив желток. Затем аккуратно погрузите половник вместе с яйцом в кипящую воду и варите 1 минуту. Выловите яйцо и срочно на блюдо!',
            cooking_time=10
        )
        IngredientInRecipe.objects.create(recipe=poached_egg, ingredient=eggs, amount=75)
        poached_egg.tags.add(breakfast_tag)


        mulled_wine = Recipe.objects.create(
            name = 'глинтвейн',
            author=user3,
            image='recipes/images/глинтвейн.jpeg',
            text='Закиньте ингридиенты в вино и нагрейте на огне до 80 градусов. Желательно не закипятить. После нагрева дайте напитку настояться в закрытой кастрюле, а лучше в термосе.',
            cooking_time=15
        )
        vine =  Ingredient.objects.get(name='вино красное сладкое')
        cinnamon = Ingredient.objects.get(name='корица')
        IngredientInRecipe.objects.create(recipe=mulled_wine, ingredient=vine, amount=700)
        IngredientInRecipe.objects.create(recipe=mulled_wine, ingredient=cinnamon, amount = 10)
        IngredientInRecipe.objects.create(recipe=mulled_wine, ingredient=lemon, amount = 20)
        IngredientInRecipe.objects.create(recipe=mulled_wine, ingredient=water, amount = 300)
        mulled_wine.tags.add(drink_tag, desert_tag)

        boiled_potato = Recipe.objects.create(
            name = 'картофель в мундирах',
            author=user3,
            image='recipes/images/картофель.jpg',
            text='Тщательно помойте картофель, положите в холодную воду и варите на среднем огне пока нох не будет с легкостью протыкать картофель на 1 см в глубину. Как потыкаете, сливайте воду и тушите свет.',
            cooking_time=30
        )
        potatoes = Ingredient.objects.get(name='картофель')
        IngredientInRecipe.objects.create(recipe=boiled_potato, ingredient=potatoes, amount=1000)
        boiled_potato.tags.add(dinner_tag)

        milkcorn = Recipe.objects.create(
            name = 'Кукурузные хлопья с молоком',
            author=user3,
            image='recipes/images/хлопья.jpg',
            text='Смешать, но не взбалтывать',
            cooking_time=5
        )
        flakes = Ingredient.objects.get(name='кукурузные хлопья глазированные')
        milk = Ingredient.objects.get(name='молоко')
        IngredientInRecipe.objects.create(recipe=milkcorn, ingredient=flakes, amount=200)
        IngredientInRecipe.objects.create(recipe=milkcorn, ingredient=milk, amount=200)
        milkcorn.tags.add(breakfast_tag)

