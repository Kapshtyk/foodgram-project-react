# FoodGram

FoodGram - это онлайн-платформа, где пользователи могут создавать, просматривать и делиться рецептами. Здесь вы можете найти разнообразные рецепты, добавлять их в избранное, а также создавать список покупок для покупки необходимых ингредиентов.

## Особенности

- Регистрация и аутентификация пользователей
- Создание, редактирование и удаление рецептов
- Добавление рецептов в избранное
- Создание списка покупок и скачивание списка ингредиентов из него
- Поиск рецептов по тегам
- Загрузка изображений для рецептов

## Технологии

- Django - основной фреймворк для разработки
- Django REST Framework - использован для создания API
- PostgreSQL - база данных для хранения рецептов, пользователей и других данных
- Docker - использован для контейниризации приложения

## Установка и запуск

### Общий доступ

На настоящий момент сайт доступен по следующему адресу: [http://158.160.69.32](http://158.160.69.32/recipes)

Для доступа к части функционала необходимо зарегистрироваться, либо можно воспользоваться логином admin@admin.ru и паролем admin для доступа к сайту с правами администратора.

### Локальная версия сайта

1. Установите Docker и Docker Compose, если они еще не установлены.
2. Склонируйте репозиторий:
```
git clone https://github.com/Kapshtak/foodgram-project-react.git
```
3. Перейдите в папку проекта, содержащие файлы для настройки инфраструктуры:
```
cd foodgram-project-react/infra
```
4. На базе находящегося там файла `.env.example` создайте свой файл для подключения к базе данных.
5. Осуществите сборку и запуск контейнеров (во время этого этапа будут развернуты 4 контейнера, внутри контейнера с бэкэндом будут применены миграции, а в базу данных будут загружены данные):
```
docker-compose build
docker-compose up
```
6.    Для наполнения локальной версии сайта контентом необходимо ввести в терминале следующие команды:
```
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py loaddata database.json
```

7. Сайт будет доступен по адресу [localhost](localhost). Для доступа к сайту необходимо зарегистрироваться через специальную форму, находящуюся по адресу [localhost/signup](http://localhost/signup). Для доступа к панели администратора необходимо создать суперюзера, для чего в терминале необходимо набрать
`docker-compose exec backend python manage.py createsuperuser`, после чего заполнить необходимые поля, либо можно воспользоваться логином admin@admin.ru и паролем admin.

## Скриншот сайта

![desktop](https://github.com/Kapshtak/foodgram-project-react/blob/master/screenshots/recipes.png?raw=true)

## Благодарности

- Изображения, использованные в этом проекте, были взяты с сайтов [Unsplash](https://unsplash.com/), [Freepik](https://www.freepik.com/) и [Pexels](https://www.pexels.com)

## Автор
- LinkedIn - [Арсений Капштык](https://www.linkedin.com/in/kapshtyk/)
- Github - [@kapshtak](https://github.com/Kapshtak)
