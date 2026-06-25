from flask import Flask, render_template, request, session, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = "cafe123"

menu = [
    {"name": "Veg Fried Rice", "price": 60, "image": "veg_fried_rice.jpg"},
    {"name": "Veg Noodles", "price": 60, "image": "veg_noodles.jpg"},
    {"name": "Veg Manchurian", "price": 70, "image": "veg_manchurian.jpg"},
    {"name": "Veg Manchurian Rice", "price": 70, "image": "veg_manchurian_rice.jpg"},
    {"name": "Veg Manchurian Noodles", "price": 70, "image": "veg_manchurian_noodles.jpg"},
    {"name": "Jeera Rice", "price": 70, "image": "jeera_rice.jpg"},
    {"name": "Tomato Rice", "price": 80, "image": "tomato_rice.jpg"},

    {"name": "Egg Fried Rice", "price": 70, "image": "egg_fried_rice.jpg"},
    {"name": "Egg Noodles", "price": 70, "image": "egg_noodles.jpg"},
    {"name": "Double Egg Fried Rice", "price": 80, "image": "double_egg_fried_rice.jpg"},
    {"name": "Double Egg Noodles", "price": 80, "image": "double_egg_noodles.jpg"},
    {"name": "Chicken Fried Rice", "price": 80, "image": "chicken_fried_rice.jpg"},
    {"name": "Chicken Noodles", "price": 80, "image": "chicken_noodles.jpg"},
    {"name": "Egg + Veg Manchurian Fried Rice", "price": 80, "image": "egg_veg_manchurian_fried_rice.jpg"},
    {"name": "Egg + Veg Manchurian Noodles", "price": 80, "image": "egg_veg_manchurian_noodles.jpg"},
    {"name": "Double Egg Chicken Fried Rice", "price": 90, "image": "double_egg_chicken_fried_rice.jpg"},
    {"name": "Double Egg Chicken Noodles", "price": 90, "image": "double_egg_chicken_noodles.jpg"},
    {"name": "Chicken Manchurian", "price": 120, "image": "chicken_manchurian.jpg"},
]

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("orders.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            address TEXT,
            items TEXT,
            total INTEGER,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------
@app.route("/")
def menu_page():
    return render_template("menu.html", menu=menu)

# ---------------- CART ----------------
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    item = request.form["item"]
    price = int(request.form["price"])

    if "cart" not in session:
        session["cart"] = []

    session["cart"].append({"item": item, "price": price})
    session.modified = True

    return redirect("/")

@app.route("/cart")
def cart():
    cart = session.get("cart", [])
    total = sum(i["price"] for i in cart)
    return render_template("cart.html", cart=cart, total=total)

# ---------------- PLACE ORDER ----------------
@app.route("/place_order", methods=["POST"])
def place_order():

    cart = session.get("cart", [])

    if cart:
        total = sum(i["price"] for i in cart)

        name = request.form["name"]
        phone = request.form["phone"]
        address = request.form["address"]

        conn = sqlite3.connect("orders.db")
        c = conn.cursor()

        c.execute("""
            INSERT INTO orders (name, phone, address, items, total, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, phone, address, str(cart), total, "Pending"))

        conn.commit()
        conn.close()

        session.pop("cart", None)

    return redirect("/admin")

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():

    conn = sqlite3.connect("orders.db")
    c = conn.cursor()

    c.execute("SELECT * FROM orders ORDER BY id DESC")
    rows = c.fetchall()

    conn.close()

    orders = []

    for r in rows:
        orders.append({
            "id": r[0],
            "name": r[1],
            "phone": r[2],
            "address": r[3],
            "items": eval(r[4]),
            "total": r[5],
            "status": r[6]
        })

    return render_template("admin.html", orders=orders)

# ---------------- STATUS UPDATE ----------------
@app.route("/update_status/<int:id>", methods=["POST"])
def update_status(id):

    new_status = request.form["status"]

    conn = sqlite3.connect("orders.db")
    c = conn.cursor()

    c.execute("UPDATE orders SET status=? WHERE id=?", (new_status, id))

    conn.commit()
    conn.close()

    return redirect("/admin")
@app.route("/kitchen")
def kitchen():

    conn = sqlite3.connect("orders.db")
    c = conn.cursor()

    c.execute("SELECT id, items, status FROM orders ORDER BY id DESC")
    rows = c.fetchall()

    conn.close()

    orders = []

    for r in rows:
        orders.append({
            "id": r[0],
            "items": eval(r[1]),
            "status": r[2]
        })

    return render_template("kitchen.html", orders=orders)
@app.route("/bill/<int:id>")
def bill(id):

    conn = sqlite3.connect("orders.db")
    c = conn.cursor()

    c.execute("SELECT * FROM orders WHERE id=?", (id,))
    row = c.fetchone()

    conn.close()

    order = {
        "id": row[0],
        "name": row[1],
        "phone": row[2],
        "address": row[3],
        "items": eval(row[4]),
        "total": row[5],
        "status": row[6]
    }

    return render_template("bill.html", order=order)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)