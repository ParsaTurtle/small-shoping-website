from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ===== دیتابیس =====
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(300), nullable=True)
    image = db.Column(db.String(300), nullable=True)

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(100), nullable=False, default="فروشگاه من")
    logo_url = db.Column(db.String(300), nullable=True)

# ===== ساخت دیتابیس =====
with app.app_context():
    db.create_all()

# ===== سبد خرید موقت =====
cart = []

# ===== CSS حرفه‌ای =====
home_html_css = """
body {font-family:'Vazir', Tahoma, sans-serif; background:#f0f2f5; margin:0; padding:0;}
header {background:#007bc7; color:white; padding:15px 20px; display:flex; align-items:center; justify-content:space-between; box-shadow:0 2px 5px rgba(0,0,0,0.2);}
header img {height:50px; margin-left:10px;}
header h1 {margin:0; font-size:20px;}
nav a {color:white; text-decoration:none; margin-left:15px; font-weight:bold; transition:0.3s;}
nav a:hover {color:#ffe082;}
.container {display:flex; flex-wrap:wrap; justify-content:center; padding:20px;}
.card {background:white; width:220px; margin:15px; border-radius:15px; box-shadow:0 6px 15px rgba(0,0,0,0.15); transition:0.4s;}
.card:hover {transform:translateY(-7px) scale(1.03); box-shadow:0 10px 25px rgba(0,0,0,0.25);}
.card img {width:100%; height:180px; object-fit:cover; border-top-left-radius:15px; border-top-right-radius:15px;}
.card-content {padding:15px;}
.card-content h3 {margin:5px 0; font-size:16px; color:#222; height:40px; overflow:hidden;}
.card-content p {font-size:13px; color:#555; height:40px; overflow:hidden;}
.card-content span {font-weight:bold; color:#d32f2f; font-size:15px;}
button {background:#ff6f00; color:white; border:none; padding:8px 10px; border-radius:8px; cursor:pointer; width:100%; font-weight:bold; transition:0.3s;}
button:hover {background:#e65100;}
@media (max-width:768px){
  .container {flex-direction:column; align-items:center;}
  .card {width:90%;}
}
"""

admin_html_css = """
body {font-family:'Vazir', Tahoma, sans-serif; background:#f0f2f5; margin:0; padding:0;}
header {background:#007bc7; color:white; padding:15px 20px; display:flex; align-items:center; justify-content:space-between; box-shadow:0 2px 5px rgba(0,0,0,0.2);}
header img {height:50px; margin-left:10px;}
header h1 {margin:0; font-size:20px;}
nav a {color:white; text-decoration:none; margin-left:15px; font-weight:bold; transition:0.3s;}
nav a:hover {color:#ffe082;}
.container {padding:20px; max-width:900px; margin:auto;}
form {background:white; padding:20px; margin-bottom:20px; border-radius:15px; box-shadow:0 4px 12px rgba(0,0,0,0.1);}
input, button {width:100%; padding:12px; margin:5px 0; border-radius:8px; font-size:14px;}
button {background:#43a047; color:white; border:none; cursor:pointer; font-weight:bold; transition:0.3s;}
button:hover {background:#2e7d32;}
.product-list {margin-top:20px;}
.product-item {background:white; padding:15px; margin-bottom:12px; border-radius:12px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 4px 12px rgba(0,0,0,0.1); transition:0.3s;}
.product-item:hover {transform:translateY(-3px); box-shadow:0 6px 18px rgba(0,0,0,0.2);}
.product-item button {background:#d32f2f;}
.product-item button:hover {background:#b71c1c;}
@media (max-width:768px){
  .container {padding:10px;}
  .product-item {flex-direction:column; align-items:flex-start;}
}
"""

# ===== HTML صفحه اصلی =====
home_html = """
<!DOCTYPE html>
<html lang="fa">
<head>
<meta charset="UTF-8">
<title>{{setting.store_name}}</title>
<style>
""" + home_html_css + """
</style>
</head>
<body>
<header>
<div style="display:flex; align-items:center;">
{% if setting.logo_url %}<img src="{{setting.logo_url}}">{% endif %}
<h1>{{setting.store_name}}</h1>
</div>
<nav>
<a href="{{ url_for('home') }}">خانه</a>
<a href="{{ url_for('show_cart') }}">سبد خرید</a>
<a href="{{ url_for('admin_panel') }}">پنل مدیریت</a>
</nav>
</header>
<div class="container">
{% for product in products %}
<div class="card">
<img src="{{product.image if product.image else 'https://via.placeholder.com/220x180'}}">
<div class="card-content">
<h3>{{product.name}}</h3>
<p>{{product.description}}</p>
<p><span>{{product.price}} تومان</span></p>
<form action="{{ url_for('add_to_cart') }}" method="post">
<input type="hidden" name="id" value="{{product.id}}">
<button>افزودن به سبد خرید</button>
</form>
</div>
</div>
{% endfor %}
</div>
</body>
</html>
"""

# ===== HTML پنل مدیریت =====
admin_html = """
<!DOCTYPE html>
<html lang="fa">
<head>
<meta charset="UTF-8">
<title>پنل مدیریت - {{setting.store_name}}</title>
<style>
""" + admin_html_css + """
</style>
</head>
<body>
<header>
<div style="display:flex; align-items:center;">
{% if setting.logo_url %}<img src="{{setting.logo_url}}">{% endif %}
<h1>{{setting.store_name}}</h1>
</div>
<nav>
<a href="{{ url_for('home') }}">خانه</a>
<a href="{{ url_for('show_cart') }}">سبد خرید</a>
<a href="{{ url_for('admin_panel') }}">پنل مدیریت</a>
</nav>
</header>
<div class="container">
<h2>تنظیمات فروشگاه</h2>
<form action="{{ url_for('update_setting') }}" method="post">
<input type="text" name="store_name" placeholder="نام فروشگاه" value="{{setting.store_name}}" required>
<input type="text" name="logo_url" placeholder="لینک لوگو" value="{{setting.logo_url}}">
<button>ذخیره تنظیمات</button>
</form>

<h2>افزودن محصول جدید</h2>
<form action="{{ url_for('add_product') }}" method="post">
<input type="text" name="name" placeholder="نام محصول" required>
<input type="text" name="description" placeholder="توضیح محصول">
<input type="number" name="price" placeholder="قیمت" required>
<input type="text" name="image" placeholder="لینک تصویر">
<button>افزودن محصول</button>
</form>

<h2>محصولات موجود</h2>
<div class="product-list">
{% for p in products %}
<div class="product-item">
<div>{{p.name}} - {{p.price}} تومان</div>
<form action="{{ url_for('delete_product') }}" method="post">
<input type="hidden" name="id" value="{{p.id}}">
<button>حذف</button>
</form>
</div>
{% endfor %}
</div>
</div>
</body>
</html>
"""

# ===== HTML سبد خرید =====
cart_html = """
<!DOCTYPE html>
<html lang="fa">
<head>
<meta charset="UTF-8">
<title>سبد خرید - {{setting.store_name}}</title>
<style>
body {font-family:'Vazir', Tahoma, sans-serif; background:#f5f5f5; margin:0; padding:0;}
header {background:#007bc7; color:white; padding:15px 20px; display:flex; align-items:center; justify-content:space-between;}
header img {height:50px; margin-left:10px;}
header h1 {margin:0;}
nav a {color:white; text-decoration:none; margin-left:15
px; font-weight:bold;}
.container {padding:20px;}
table {margin:20px auto; border-collapse: collapse; width:90%;}
td, th {border:1px solid #ccc; padding:10px; text-align:center;}
button {background:#d32f2f; color:white; border:none; padding:6px 10px; cursor:pointer; border-radius:5px;}
button:hover {background:#b71c1c;}
</style>
</head>
<body>
<header>
<div style="display:flex; align-items:center;">
{% if setting.logo_url %}<img src="{{setting.logo_url}}">{% endif %}
<h1>{{setting.store_name}}</h1>
</div>
<nav>
<a href="{{ url_for('home') }}">خانه</a>
<a href="{{ url_for('show_cart') }}">سبد خرید</a>
<a href="{{ url_for('admin_panel') }}">پنل مدیریت</a>
</nav>
</header>
<div class="container">
<h2 style="text-align:center;">سبد خرید شما</h2>
<table>
<tr><th>محصول</th><th>قیمت</th><th>عملیات</th></tr>
{% for item in cart %}
<tr>
<td>{{item.name}}</td>
<td>{{item.price}}</td>
<td>
<form action="{{ url_for('remove_from_cart') }}" method="post">
<input type="hidden" name="id" value="{{item.id}}">
<button>حذف</button>
</form>
</td>
</tr>
{% endfor %}
</table>
{% if cart|length > 0 %}
<p style="text-align:center; font-weight:bold;">جمع کل: {{cart|sum(attribute='price')}} تومان</p>
{% else %}
<p style="text-align:center;">سبد خرید خالی است</p>
{% endif %}
</div>
</body>
</html>
"""

# ===== مسیرهای Flask =====
@app.route('/')
def home():
    products = Product.query.all()
    setting = Setting.query.first()
    return render_template_string(home_html, products=products, setting=setting)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    prod_id = int(request.form['id'])
    product = Product.query.get(prod_id)
    if product:
        cart.append(product)
    return redirect('/')

@app.route('/cart')
def show_cart():
    setting = Setting.query.first()
    return render_template_string(cart_html, cart=cart, setting=setting)

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    prod_id = int(request.form['id'])
    global cart
    cart = [c for c in cart if c.id != prod_id]
    return redirect('/cart')

@app.route('/admin')
def admin_panel():
    products = Product.query.all()
    setting = Setting.query.first()
    return render_template_string(admin_html, products=products, setting=setting)

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    description = request.form['description']
    price = int(request.form['price'])
    image = request.form['image']
    new_product = Product(name=name, description=description, price=price, image=image)
    db.session.add(new_product)
    db.session.commit()
    return redirect('/admin')

@app.route('/admin/delete_product', methods=['POST'])
def delete_product():
    prod_id = int(request.form['id'])
    product = Product.query.get(prod_id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return redirect('/admin')

@app.route('/admin/update_setting', methods=['POST'])
def update_setting():
    setting = Setting.query.first()
    if not setting:
        setting = Setting()
        db.session.add(setting)
    setting.store_name = request.form['store_name']
    setting.logo_url = request.form['logo_url']
    db.session.commit()
    return redirect('/admin')

# ===== اجرا =====
if __name__ == '__main__':
    app.run(debug=True)
