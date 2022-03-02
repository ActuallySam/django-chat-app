# Django Chat Application

To run the backend, run:

```
virtualenv evnv
source venv/bin/activate
pip3 install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```

To develop locally:

```
1. Create two users (easiest way might be to run `python manage.py createsuperuser` twice)
2. Using django admin, create a `Contact` object for each user.
3. Make sure you have an instance of redis running, by running the command below: (Make sure you install Docker first)    
```
```
                                      docker run -p 6379:6379 -d redis:5
```
         

Please note this is a **demo project** of the concepts used in building a chat app. It is simply not production ready. For example, when the backend receives a message, it'll broadcast to everyone in the room including the sender. This means when you demo the sender role, be aware you'll see every outbound message duplicated. The project is setup for deployment on Heroku however you'll need to follow tutorials on how to get this [up and running](https://blog.heroku.com/in_deep_with_django_channels_the_future_of_real_time_apps_in_django)
