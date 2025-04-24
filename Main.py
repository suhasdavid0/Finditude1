from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from sqlalchemy import text
from sqlalchemy import create_engine
import pandas as pd
from config import DATABASE_CONFIG
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import session
from flask_mail import Mail, Message

app = Flask(__name__)
api = Api(app)
app.secret_key = 'super_secret_key'
DATABASE_URL = f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}/{DATABASE_CONFIG['database']}"
engine = create_engine(DATABASE_URL)

#Mail Config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'moori.ahmad1997@gmail.com'
app.config['MAIL_PASSWORD'] = 'rzbjhuyvkehnsram'
mail = Mail(app)

class Home(Resource):
    def get(self):
        return {"message": "Flask backend is running!"}

class GetRecommendations(Resource):
    def get(self):
        category = request.args.get("type")  
        zip_code = request.args.get("zip")  

        if zip_code and category:
            #GET http://127.0.0.1:5000/api/demo?type=restaurant&zip=63108
            zip_code = int(zip_code) 

            query = """
                SELECT *, ABS(zip - %s) AS distance 
                FROM demo 
                WHERE LOWER(primary_category_name) LIKE LOWER(%s) 
                ORDER BY distance 
                LIMIT 2;
            """
            df = pd.read_sql(query, engine, params=(zip_code, f"%{category}%"))

            if df.empty:
                return jsonify({"message": "No nearby options found for this category."})
        
        elif category:
            #GET http://127.0.0.1:5000/api/demo?type=restaurant
            query = "SELECT * FROM demo WHERE LOWER(primary_category_name) LIKE LOWER(%s);"
            df = pd.read_sql(query, engine, params=(f"%{category}%",))

            if df.empty:
                return jsonify({"message": "No options available for this category."})

    
            df = df.sample(n=2, replace=False) if len(df) >= 2 else df

            return jsonify(df.to_dict(orient="records"))
        
        else:
            
            query = "SELECT * FROM demo;"
            df = pd.read_sql(query, engine)
            if df.empty:
                return jsonify({"message": "No options available."})

        
        if "zip_code" not in locals():  
            df = df.sample(n=2, replace=False) if len(df) >= 2 else df
        
        return jsonify(df.to_dict(orient="records"))

@app.route("/signup", methods=["POST"])
def signup():
    # POST http://127.0.0.1:5000/signup
    if request.is_json:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        full_name = data.get("full_name")
        email = data.get("email")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        full_name = request.form.get("full_name")
        email = request.form.get("email")

    if not username or not password or not full_name or not email:
        return jsonify({"error": "All fields are required."}), 400

    # Check for existing user
    check_query = "SELECT * FROM users WHERE username = %s;"
    existing_user = pd.read_sql(check_query, engine, params=(username,))
    if not existing_user.empty:
        return jsonify({"error": "Username already exists."}), 409

    # Hash password
    password_hash = generate_password_hash(password)

    # Insert into DB
    insert_query = """
        INSERT INTO users (username, password_hash, full_name, email)
        VALUES (:username, :password_hash, :full_name, :email)
    """
    with engine.begin() as connection:
        connection.execute(
            text(insert_query),
            {
                "username": username,
                "password_hash": password_hash,
                "full_name": full_name,
                "email": email
            }
        )

    return jsonify({"message": "User registered successfully!"}), 201
    
@app.route("/login", methods=["POST"])
def login():
    if request.is_json:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    query = "SELECT * FROM users WHERE username = %s;"
    user_df = pd.read_sql(query, engine, params=(username,))

    if user_df.empty:
        return jsonify({"error": "Invalid username or password."}), 401

    stored_hash = user_df.iloc[0]["password_hash"]
    if not check_password_hash(stored_hash, password):
        return jsonify({"error": "Invalid username or password."}), 401

    session['user_id'] = int(user_df.iloc[0]["id"])
    user_fullname = user_df.iloc[0]["full_name"]
    user_email = user_df.iloc[0]["email"]
    return jsonify({"message": "Login successful!"}), 200

@app.route("/send-email", methods=["POST"])
def send_email():

    if request.is_json:
        data = request.get_json()
        recipient = data.get("to")
    else:
        recipient = request.form.get("to")

    msg = Message(
        subject="Hello from Finditude!",
        sender=app.config['MAIL_USERNAME'],
        recipients=[recipient],
        body="This is a test email sent from Finditude app 💌"
    )

    mail.send(msg)
    return jsonify({"message": "Email sent successfully!"}), 200

api.add_resource(Home, "/")
api.add_resource(GetRecommendations, "/api/demo")  

if __name__ == "__main__":
    app.run(debug=True)
