import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/products_img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# MySQL configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'furniture',
}

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to insert a new product into the MySQL database
def insert_product_to_database(name, description, image):
    try:
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Query to insert the product into the "products" table
        query = "INSERT INTO products (name, description, image) VALUES (%s, %s, %s);"
        values = (name, description, image)
        cursor.execute(query, values)

        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print("Error inserting product:", e)
        return False

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Products page
@app.route('/products')
def show_products():
    # Fetch products from the database
    try:
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Query to fetch products from the "products" table
        query = "SELECT name, description, image FROM products;"
        cursor.execute(query)
        products = []
        for (name, description, image) in cursor:
            products.append({
                'name': name,
                'description': description,
                'image':  image,
            })

        cursor.close()
        connection.close()
        return render_template('products.html', products=products)
    except Exception as e:
        print("Error fetching products:", e)
        return render_template('products.html', products=[])

# Add Product page
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image = request.files['image']

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Save only the name of the image file to the database
            image_name = filename

            if insert_product_to_database(name, description, image_name):
                return redirect(url_for('show_products'))
            else:
                return "Error inserting product into the database."

    return render_template('add_product.html')

if __name__ == '__main__':
    app.run(debug=True)