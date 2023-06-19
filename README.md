[![Django-app workflow](https://github.com/Kapshtak/foodgram-project-react/actions/workflows/foodgram-workflow.yml/badge.svg?branch=master)](https://github.com/Kapshtak/foodgram-project-react/actions/workflows/foodgram-workflow.yml)
# FoodGram

FoodGram is an online platform where users can create, view, and share recipes. Here, you can find a wide variety of recipes, add them to your favorites, and create a shopping list to purchase the necessary ingredients.

## Features

- User registration and authentication
- Recipe creation, editing, and deletion
- Adding recipes to favorites
- Creating a shopping list and downloading the ingredient list
- Recipe search by tags
- Uploading images for recipes

## Technologies

- Django - the main framework used for development
- Django REST Framework - used for creating the API
- PostgreSQL - the database for storing recipes, users, and other data
- Docker - used for containerizing the application

## Installation and Setup

### Public Access

Currently, the website is accessible at the following address: [http://158.160.69.32](http://158.160.69.32/recipes)

To access certain functionalities, you need to register. Alternatively, you can use the login admin@admin.ru with the password admin to access the site with administrator rights.

### Local Deployment

1. Install Docker and Docker Compose if you haven't already.
2. Clone the repository:
```
git clone https://github.com/Kapshtak/foodgram-project-react.git
```
3. Navigate to the project folder containing the infrastructure setup files:
```
cd foodgram-project-react/infra
```
4. Create your own `.env` file based on the provided `.env.example` file for connecting to the database.
5. Build and launch the containers:
```
docker-compose build
docker-compose up
```
6. To populate the local version of the website with content, run the following commands in the terminal:
```
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py loaddata database.json
```
7. The website will be accessible at [localhost](localhost). To access the site, register through the provided form at [localhost/signup](localhost/signup). To access the admin panel, create a superuser by running the command `docker-compose exec backend python manage.py createsuperuser` in the terminal. Alternatively, you can use the login `admin@admin.ru` with the password `admin` to access the admin panel.
## Website Screenshot

![desktop](https://github.com/Kapshtak/foodgram-project-react/blob/master/screenshots/recipes.png?raw=true)

## Acknowledgments

- Images used in this project were obtained from [Unsplash](https://unsplash.com/), [Freepik](https://www.freepik.com/), and [Pexels](https://www.pexels.com)

## Author
- LinkedIn - [Arseny Kapshtyk](https://www.linkedin.com/in/kapshtyk/)
- Github - [@kapshtak](https://github.com/Kapshtak)
