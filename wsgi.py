# a simple wsgi script to run the flask application using gunicorn

from app import create_app, db
from app.models import User

# initialize the app
app = create_app()

# push the app context
# see https://flask-sqlalchemy.palletsprojects.com/en/2.x/contexts/
app.app_context().push()

# initialize the database
db.create_all(app=create_app())

# create default user
initial_user = User(
                id=1,
                username='libreforms', 
                password='pbkdf2:sha256:260000$nQVWxd59E8lmkruy$13d8c4d408185ccc3549d3629be9cd57267a7d660abef389b3be70850e1bbfbf',
                created_date='2022-06-01 00:00:00',
        )

db.session.add(initial_user)
db.session.commit()



if __name__ == "__main__":
        app.run()



