from flask import Flask, jsonify, render_template, request
from models.cafe import Cafe, db
import random


'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db.init_app(app)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record

# HTTP POST - Create Record
# Prompt specified that the request was sent from
# Postman as 'x-www-form-urlencoded', so we are
# receiving this as form data and not request.args.
@app.route("/add", methods=["POST"])
def add():
    new_cafe = Cafe(
        name=request.form["name"],
        map_url=request.form["map_url"],
        img_url=request.form["img_url"],
        location=request.form["location"],
        seats=request.form["seats"],
        has_toilet=bool(int(request.form["has_toilet"])),
        has_wifi=bool(int(request.form["has_wifi"])),
        has_sockets=bool(int(request.form["has_sockets"])),
        can_take_calls=bool(int(request.form["can_take_calls"])),
        coffee_price=request.form["coffee_price"]
    )
    with app.app_context():
        db.session.add(new_cafe)
        db.session.commit()

    return jsonify(
        {
            "response": {
                "success": "Successfully added the new cafe."
            }
        }
    )


# HTTP PUT/PATCH - Update Record
# Opposed to the /add route, the updated coffee_price
# is sent as a request parameter, so we receive it
# in request.args. From Postman this is sent as a
# PATCH request. This route will not work in a browser
# unless you add "GET" to the route's methods parameter
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    with app.app_context():
        cafe_to_update = db.session.get(Cafe, cafe_id)
        if not cafe_to_update:
            return jsonify(
                error={
                    "Not Found": "Sorry, a cafe with that id was not found in the database."
                }
            ), 404  # Pass the error code. Otherwise, you'll still get a 200 OK response.
        else:
            cafe_to_update.coffee_price = new_price
            db.session.commit()
            return jsonify(
                {
                    "success": "Successfully updated the price."
                }
            ), 200  # Not necessary to pass the response code here, but I did it for consistency.
# HTTP DELETE - Delete Record


@app.route("/all")
def get_all_cafes():
    with app.app_context():
        all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
    cafes_json_list = [cafe.to_dict() for cafe in all_cafes]
    return jsonify(cafes=cafes_json_list)


@app.route("/random")
def get_random_cafe():
    row_count = db.session.query(Cafe).count()
    random_row_id = random.randint(1, row_count)
    with app.app_context():
        random_cafe = db.get_or_404(Cafe, random_row_id)
    # The long way to create a dict to jsonify, but you'd have to repeat this
    # or similar code block in other routes.
    # cafe_data = {
    #     "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #     "seats": random_cafe.seats,
    #     "has_toilet": random_cafe.has_toilet,
    #     "has_wifi": random_cafe.has_wifi,
    #     "has_sockets": random_cafe.has_sockets,
    #     "can_take_calls": random_cafe.can_take_calls,
    #     "coffee_price": random_cafe.coffee_price
    # }
    # return jsonify(
    #     cafe=cafe_data
    # )

    # Instead, create a method in the Cafe class that returns a dict.
    # See ./models/cafe.py
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/search")
def search():
    loc = request.args["loc"]
    with app.app_context():
        cafes_by_user_loc = db.session.execute(db.select(Cafe).where(Cafe.location == loc)).scalars().all()

        if not cafes_by_user_loc:
            return jsonify(
                {
                    "error": {
                        "Not Found": " Sorry, we don't have a cafe at that location"
                    }
                }
            )
        else:
            cafes_by_user_loc_list = [cafe.to_dict() for cafe in cafes_by_user_loc]
            return jsonify(cafes=cafes_by_user_loc_list)


if __name__ == '__main__':
    app.run(debug=True)
