from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database_setup import DBSession, Restaurant, MenuItem

app = Flask(__name__)


@app.route("/")
@app.route("/restaurants/", methods=["GET"])
def restaurants():
    with DBSession() as sess:
        restaurant = sess.query(Restaurant).all()
    return render_template("restaurants.html", restaurant=restaurant)


@app.route("/restaurants/<int:restaurant_id>/json", methods=["GET"])
def restaurant_json(restaurant_id):
    with DBSession() as sess:
        restaurant = sess.query(Restaurant).filter_by(id=restaurant_id).one()
    return jsonify(restaurant.serialize())


@app.route("/restaurants/<int:restaurant_id>/", methods=["GET"])
@app.route("/restaurants/<int:restaurant_id>/menu", methods=["GET"])
def restaurant(restaurant_id):
    with DBSession() as sess:
        restaurant = sess.query(Restaurant).filter_by(id=restaurant_id).one()
        menuitems = sess.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template("menu.html", restaurant=restaurant, menuitems=menuitems)


@app.route("/restaurants/<int:restaurant_id>/menu/json", methods=["GET"])
def restaurant_menu_json(restaurant_id):
    with DBSession() as sess:
        restaurant = sess.query(Restaurant).filter_by(id=restaurant_id).one()
        menuitems = sess.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return jsonify(list(item.serialize() for item in menuitems))


@app.route("/restaurants/<int:restaurant_id>/edit", methods=["GET", "POST"])
def restaurant_edit(restaurant_id):
    if request.method == "POST":
        with DBSession() as sess:
            restaurant = sess.query(Restaurant).filter_by(restaurant_id=restaurant_id).one()
            restaurant.name = request.form.get('name')
        flash("Restaurant has been renamed")
        return redirect(url_for('restaurant', restaurant_id=restaurant_id,))
    else:
        with DBSession() as sess:
            restaurant = sess.query(Restaurant).filter_by(restaurant_id=restaurant_id).one()
        return render_template("editrestaurant.html", restaurant=restaurant)


@app.route("/restaurants/<int:restaurant_id>/new", methods=["GET", "POST"])
def menu_item_new(restaurant_id):
    if request.method == "POST":
        with DBSession() as sess:
            menuitem = MenuItem()
            menuitem.restaurant_id = restaurant_id
            menuitem.name = request.form.get('name')
            menuitem.price = request.form.get('price')
            menuitem.description = request.form.get('description')
            menuitem.course = request.form.get('course')
            sess.add(menuitem)
        flash("The new menu item has been created")
        return redirect(url_for('restaurant', restaurant_id=restaurant_id))
    else:
        return render_template("newmenuitem.html", restaurant_id=restaurant_id)


@app.route("/restaurants/<int:restaurant_id>/menu/<int:menu_id>/json", methods=["GET"])
def menu_item_json(restaurant_id, menu_id):
    with DBSession() as sess:
        menuitem = sess.query(MenuItem).filter_by(restaurant_id=restaurant_id).filter_by(id=menu_id).one()
    return jsonify(menuitem.serialize())


@app.route("/restaurants/<int:restaurant_id>/<int:menu_id>/edit", methods=["GET", "POST"])
@app.route("/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit", methods=["GET", "POST"])
def menu_item_edit(restaurant_id, menu_id):
    if request.method == "POST":
        with DBSession() as sess:
            menuitem = sess.query(MenuItem).filter_by(restaurant_id=restaurant_id).filter_by(id=menu_id).one()
            menuitem.name = request.form.get('name')
            menuitem.price = request.form.get('price')
            menuitem.description = request.form.get('description')
            menuitem.course = request.form.get('course')
        flash("Menu item has been edited")
        return redirect(url_for('restaurant', restaurant_id=restaurant_id))
    else:
        with DBSession() as sess:
            menuitem = sess.query(MenuItem).filter_by(restaurant_id=restaurant_id).filter_by(id=menu_id).one()
        return render_template("editmenuitem.html", restaurant_id=restaurant_id, menuitem=menuitem)


@app.route("/restaurants/<int:restaurant_id>/<int:menu_id>/delete", methods=["GET", "POST"])
@app.route("/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete", methods=["GET", "POST"])
def menu_item_delete(restaurant_id, menu_id):
    if request.method == "POST":
        with DBSession() as sess:
            menuitem = sess.query(MenuItem).filter_by(restaurant_id=restaurant_id).filter_by(id=menu_id).one()
            sess.delete(menuitem)
        flash("Menu item has been deleted")
        return redirect(url_for('restaurant', restaurant_id=restaurant_id))
    else:
        with DBSession() as sess:
            menuitem = sess.query(MenuItem).filter_by(restaurant_id=restaurant_id).filter_by(id=menu_id).one()
        return render_template("deletemenuitem.html", restaurant_id=restaurant_id, menuitem=menuitem)


if __name__ == "__main__":
    app.secret_key = "very_secret_key"
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
