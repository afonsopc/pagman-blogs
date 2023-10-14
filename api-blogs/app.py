import flask
import sqlite3
import flask_mail
import json
import os
import string
import random
import hashlib
import flask_jwt_extended
import datetime
import time
import uuid
import io
import bs4
import base64
import re
import flask_cors

# Get the path of the current script and set the working directory to that path.
script_path = __file__[:__file__.rfind("/")]
os.chdir(script_path)

# Load configuration details from a JSON file named "config.json".
with open("config.json") as f:
    config = json.load(f)

# Create a new Flask app with the name specified in the configuration file.
app = flask.Flask(config["APP_NAME"])
flask_cors.CORS(app, resources={r"/*": {"origins": "https://blogs.pagman.org"}})

# Create a new blueprint for the API with the name and URL prefix specified in the configuration file.
api_v1_bp = flask.Blueprint('api_v1', config["APP_NAME"], url_prefix=config["API_URL_PREFIX"])

# Set up configuration details for the email server.
app.config["MAIL_SERVER"] = config["MAIL_SERVER"]
app.config["MAIL_USERNAME"] = config["MAIL_ADRESS"]
app.config["MAIL_PASSWORD"] = config["MAIL_PASSWORD"]
app.config["MAIL_DEFAULT_SENDER"] = (config["MAIL_USERNAME"], config["MAIL_ADRESS"])
app.config["MAIL_PORT"] = config["MAIL_PORT"]
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

# Set up configuration details for the JWTs.
app.config["JWT_SECRET_KEY"] = config["SECRET_KEY"]
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=7)

# Set the name of the SQLite database file to the name specified in the configuration file.
db_file_name = config["DB_FILE_NAME"]

# Create a new instance of the Flask-Mail extension with the app as a parameter.
mail = flask_mail.Mail(app)

# Create a new instance of the Flask-JWT-Extended extension with the app as a parameter.
jwt = flask_jwt_extended.JWTManager(app)

def get_db():
    """
    Function to get a connection to the SQLite database.

    Returns:
    db: sqlite3.Connection
        A connection to the SQLite database.
    """

    # Get the database connection from the Flask global variable "g".
    db = getattr(flask.g, "_database", None)

    # If no database connection exists in the Flask global variable "g", create a new connection and set it as a
    # variable in "g".
    if db is None:
        db = flask.g._database = sqlite3.connect(db_file_name)
        db.row_factory = sqlite3.Row

    # Return the database connection.
    return db

@app.teardown_appcontext
def close_connection(exception):
    """
    Function to close the database connection at the end of a request.

    Parameters:
    exception: Exception
        The exception object raised by the previous function in the request stack.
    """

    # Get the database connection from the Flask global variable "g".
    db = getattr(flask.g, "_database", None)

    # If a connection to the database exists in the Flask global variable "g", close the connection.
    if db is not None:
        db.close()

def create_tables():
    """
    Function to create the database tables if they do not exist.
    The function creates the following tables:
        * confirmed_users: a table for storing confirmed user accounts.
        * pending_confirmation: a table for storing user accounts that are awaiting confirmation.
        * operations: a table for storing user operations.
        * blogs: a table for storing blog posts.
    """

    # Define the SQL queries to create the database tables.
    tables = [
        """
            CREATE TABLE IF NOT EXISTS "confirmed_users" (
                "user_id"	            TEXT NOT NULL UNIQUE,
                "username"	            TEXT NOT NULL UNIQUE,
                "email"	                TEXT NOT NULL UNIQUE,
                "password"	            TEXT NOT NULL,
                "salt"                  BLOB NOT NULL,
                PRIMARY KEY ("user_id")
            );
        """,
        """
            CREATE TABLE IF NOT EXISTS "pending_confirmation" (
                "confirmation_id"       TEXT NOT NULL,
                "username"	            TEXT NOT NULL UNIQUE,
                "email"	                TEXT NOT NULL UNIQUE,
                "password"	            TEXT NOT NULL,
                "salt"                  BLOB NOT NULL
            );
        """,
        """
            CREATE TABLE IF NOT EXISTS "operations" (
                "operation_id"          TEXT NOT NULL UNIQUE,
                "operation"	            TEXT NOT NULL,
                "user_id"  	            TEXT NOT NULL,
                "operation_value"       TEXT NOT NULL,
                FOREIGN KEY ("user_id") REFERENCES "confirmed_users" ("user_id")
            );
        """,
        """
            CREATE TABLE IF NOT EXISTS "blogs" (
                "blog_id"               TEXT NOT NULL UNIQUE,
                "user_id"	            TEXT NOT NULL,
                "blog_title"	        TEXT NOT NULL,
                "blog_html"             TEXT NOT NULL,
                "unix_time"	            INTEGER NOT NULL,
                FOREIGN KEY ("user_id") REFERENCES "confirmed_users" ("user_id")
            );
        """
    ] 

    # Get the database connection from the Flask global variable "g".
    db = get_db()

    # Create a cursor object to execute the SQL queries.
    cursor = db.cursor()

    # Execute the SQL queries to create the database tables.
    for table in tables:
        cursor.execute(table)

    # Close the cursor object.
    cursor.close()

    # Commit the changes to the database.
    db.commit()


def create_usercontent_folder():
    """
    Try to create a new directory called USERCONTENT_FOLDER, which will be used to store user-generated content.
    If the directory already exists, print a message indicating so.
    """
    try:
        # Attempt to create a new directory using the path specified in the config file
        os.mkdir(config["USERCONTENT_FOLDER"])
    except:
        # If the directory already exists, print a message indicating so
        print("Usercontent folder already exists!")


def get_unique_id():
    """
    Returns a unique ID as a string, generated using Python's built-in uuid library.
    """
    # Call the uuid4 method to generate a new unique identifier
    # Convert the UUID object to a string before returning it
    return str(uuid.uuid4())

def get_random_file_name(digits: int) -> str:
    """
    Returns a random file name made of numbers with a specified number of digits.
    """
    # Generate a unique file name
    digits = int(digits)
    start_of_random_numbers = 10**(digits-1)
    end_of_random_numbers = 10**digits-1
    file_name = random.randint(start_of_random_numbers, end_of_random_numbers)
    file_name = str(file_name)
    return file_name

def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def find_base64_sources(html_string: str):
    """Find base64 sources in an HTML string and return a list of them.

    Args:
        html_string (str): The HTML string to search.

    Returns:
        list: A list of base64 sources found in the HTML string.
    """
    base64_sources = []  # create an empty list to store base64 sources
    soup = bs4.BeautifulSoup(html_string, "html.parser")  # parse the HTML string using BeautifulSoup
    # iterate through all the img, video, audio, and source elements in the HTML string
    for element in soup.find_all(["img", "video", "audio", "source"]):
        # if the element has a 'src' attribute and the value starts with 'data:', it is a base64 source
        if element.has_attr("src") and element["src"].startswith("data:"):
            # add the base64 source to the list
            base64_sources.append(element["src"])
    # return the list of base64 sources
    return base64_sources

def save_base64_to_file(base64_str: str, file_name_without_extension: str):
    """
    Saves base64-encoded data to a file in the user content folder.
    
    Args:
        base64_str (str): Base64-encoded data string.
        file_name_without_extension (str): File name without extension.

    Returns:
        str: File URL.
    """
    
    # Get the output directory for user content.
    output_dir = os.path.join(os.getcwd(), config["USERCONTENT_FOLDER"])

    # Extract file extension from the base64 string.
    file_extension = base64_str.split('/')[1].split(';')[0]
    
    # Decode the base64 data.
    decoded_data = base64.b64decode(base64_str.split(',')[-1])

    # Set the file name and path.
    file_name_with_extension = f"{file_name_without_extension}.{file_extension}"
    file_path = os.path.join(output_dir, file_name_with_extension)

    # Get the URL of the file.
    file_url = flask.url_for("api_v1.serve_usercontent", file_name_with_extension=file_name_with_extension, _external=True)

    # Write the decoded data to a file.
    with open(file_path, 'wb+') as f:
        f.write(decoded_data)

    # Return the URL of the saved file.
    return file_url


def hash_salt_pepper(password: str, peppers=[], salt=None):
    """
    Hashes a password using PBKDF2 with SHA-256, adds optional pepper(s) and salt, and returns the salt and hashed password.
    
    Args:
    password (str): The password to be hashed
    peppers (list): A list of pepper(s) to be added to the password. Default is an empty list.
    salt (bytes): A salt to be used in the password hashing. Default is None.
    
    Returns:
    bytes: The salt used in the password hashing
    str: The hashed password
    
    """
    # Generate a random salt if none is provided
    if salt is None:
        salt = os.urandom(32)
    
    # Add any provided peppers to the password
    for pepper in peppers:
        middle = len(password)//2
        password = password[:middle] + pepper + password[middle:]
    
    # Hash the password using PBKDF2 with SHA-256
    hash_salt_pepper_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 1000000).hex()
    
    return salt, hash_salt_pepper_password


def check_if_account_already_exists(username=None, email=None):
    """
    Checks if an account already exists in the database based on the given username or email.
    
    Args:
        username (str): The username to check.
        email (str): The email to check.
        
    Returns:
        bool: True if an account already exists with the given username or email, False otherwise.
    """
    # Get a database connection
    db = get_db()
    cursor = db.cursor()
    
    # Initialize the flags
    username_exists = False
    email_exists = False
    
    # Check if a user with the given username or email exists in the confirmed_users table
    if username is not None:
        cursor.execute("""SELECT * FROM "confirmed_users" WHERE username=?""", (username,))
        confirmed_user_username = cursor.fetchone()
        cursor.execute("""SELECT * FROM "pending_confirmation" WHERE username=?""", (username,))
        pending_user_username = cursor.fetchone()
        username_exists = confirmed_user_username or pending_user_username
    if email is not None:
        cursor.execute("""SELECT * FROM "confirmed_users" WHERE email=?""", (email,))
        confirmed_user_email = cursor.fetchone()
        cursor.execute("""SELECT * FROM "pending_confirmation" WHERE email=?""", (email,))
        pending_user_email = cursor.fetchone()
        email_exists = confirmed_user_email or pending_user_email
    
    # Return the result
    if username_exists or email_exists:
        return True
    return False


@api_v1_bp.route("/signup", methods=["POST"])
def signup_pre_confirmation():
    """
    Handle user signup requests.

    Receives a POST request with a JSON payload containing the user's `username`, `email`, and `password`.
    If the `username` and `password` are valid, check if an account with the provided `username` or `email` already exists in the database.
    If an account already exists, return an error response. If the account does not exist, generate a confirmation ID and URLs for the confirmation and cancellation of the account registration.
    Send a confirmation email to the provided email address containing the confirmation and cancellation URLs.
    Salt and hash the user's password using the `hash_salt_pepper` function and store the confirmation ID, username, email, hashed password, and salt in the "pending_confirmation" table in the database.

    Returns:
        A Flask response with a JSON payload containing a message indicating that a confirmation email was sent.
    """
    # Get the user's username, email and password from the POST request
    data = flask.request.get_json()
    username = data["username"]
    email = data["email"]
    password = data["password"]

    # Check if the username or password is missing or invalid
    if username == "" or password == "":
        return flask.jsonify({"message": "Missing or Invalid data."})

    # Check if the username is too long
    if len(username) > 50:
        return flask.jsonify({"message": "Username is too long."})

    # Check if an account with the same username or email already exists
    exists = check_if_account_already_exists(username=username, email=email)
    if exists:
        return flask.jsonify({"message": "Account already registered or waiting to be confirmed."}), 409

    # Generate a unique confirmation ID and URLs for the confirmation and cancellation pages
    confirmation_id = get_unique_id()
    confirmation_url = flask.url_for("api_v1.signup_post_confirmation", confirmation_id=confirmation_id, _external=True)
    cancel_confirmation_url = flask.url_for("api_v1.signup_cancel_confirmation", confirmation_id=confirmation_id, _external=True)

    # Send a confirmation email with the confirmation and cancellation URLs
    msg = flask_mail.Message()
    msg.subject = config["CONFIRMATION_EMAIL_SUBJECT"]
    msg.html = config["CONFIRMATION_EMAIL_BODY"] \
        .replace("««««USERNAME»»»»", username) \
        .replace("««««CONFIRMATION_URL»»»»", confirmation_url) \
        .replace("««««CANCEL_CONFIRMATION_URL»»»»", cancel_confirmation_url)
    msg.recipients = [email]
    mail.send(msg)

    # Hash the user's password with a salt and peppers
    salt, hashed_password = hash_salt_pepper(password, peppers=config["PEPPERS"])

    # Save the user's information (including the confirmation ID) in the database
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""INSERT INTO "pending_confirmation" (confirmation_id, username, email, password, salt) VALUES (?, ?, ?, ?, ?)""", (confirmation_id, username, email, hashed_password, salt,))
    cursor.close()
    db.commit()

    # Return a success message
    return flask.jsonify({"message": "Email confirmation sent, check your email (If you can't find it, look in the spam folder)."}), 200

@api_v1_bp.route("/signup/cancel/<confirmation_id>", methods=["GET"])
def signup_cancel_confirmation(confirmation_id):
    """
    Route for canceling a pending confirmation account.

    Args:
        confirmation_id (str): The unique ID of the pending confirmation account.

    Returns:
        flask.Response: A JSON response indicating whether the account was successfully canceled or not.
    """
    # Get the database connection and create a cursor.
    db = get_db()
    cursor = db.cursor()

    # Execute a DELETE query to delete the pending confirmation account with the given confirmation ID.
    cursor.execute("""DELETE FROM "pending_confirmation" WHERE confirmation_id=?""", (confirmation_id,))
    deleted_rows = cursor.rowcount

    # Close the cursor and commit the transaction.
    cursor.close()
    db.commit()

    # If no rows were deleted, then there is no pending confirmation account with this confirmation id.
    if deleted_rows <= 0:
        return flask.jsonify({"message": "Confirmation ID not found."}), 400
    # Otherwise, the account was successfully deleted.
    else:
        return flask.jsonify({"message": "Account canceled"}), 200

    
@api_v1_bp.route("/signup/<confirmation_id>", methods=["GET"])
def signup_post_confirmation(confirmation_id):
    """
    Endpoint for confirming a user's account. Takes in the confirmation ID in the URL parameter, queries the database for
    the associated account information, inserts it into the confirmed_users table and deletes it from the
    pending_confirmation table. Renders a confirmation page if the confirmation ID is valid.

    Args:
        confirmation_id (str): A unique ID that identifies the account being confirmed.

    Returns:
        Flask response: A rendered HTML template with a confirmation message if the confirmation ID is valid, otherwise a
        JSON response with an error message and status code 400.

    """

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT username, email, password, salt FROM "pending_confirmation" WHERE confirmation_id=?""", (confirmation_id,))
    account_info = cursor.fetchone()
    cursor.close()
    if account_info is not None:
        user_id = get_unique_id()
        values = (user_id, account_info[0], account_info[1], account_info[2], account_info[3])
        cursor = db.cursor()
        cursor.execute("""INSERT INTO "confirmed_users" (user_id, username, email, password, salt) VALUES (?, ?, ?, ?, ?)""", values)
        cursor.execute("""DELETE FROM "pending_confirmation" WHERE confirmation_id=?""", (confirmation_id,))
        cursor.close()
        db.commit()
        # Renders a confirmation page if the confirmation ID is valid.
        return flask.render_template_string(config["ACCOUNT_CONFIRMED_PAGE_HTML"]), 200
    else:
        # Otherwise, returns a JSON response with an error message and status code 400.
        return flask.jsonify({"message": "Confirmation ID not found."}), 400


@api_v1_bp.route("/login", methods=["POST"])
def login():
    """
    Logs in a user by checking their email and password against the database.
    If the email and password match, an access token is generated and returned.

    Returns:
        A JSON object with a message indicating whether the login was successful or not and an access token if successful.
    """

    # Get the user's email and password from the POST request
    data = flask.request.get_json()
    email = data["email"]
    password = data["password"]

    db = get_db()

    # Check if an account with this email exists in the database
    exists = check_if_account_already_exists(email=email)
    if not exists:
        return flask.jsonify({"message": "Invalid username or password."}), 400

    # Search the database for a row where the email and password match
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM "confirmed_users" WHERE email=?""", (email,))
    user = cursor.fetchone()
    cursor.close()

    # If no matching row was found, the login is invalid
    if user is None:
        return flask.jsonify({
            "message": "User not found"
        }), 404
    else:
        salt = user["salt"]
    
    # Hash the provided password with the salt from the database and compare it to the stored password
    _, hashed_password = hash_salt_pepper(password, peppers=config["PEPPERS"], salt=salt)

    # If a row was found and the passwords match, the login is successful
    if user["password"] == hashed_password:
        # Generate an access token with the user's username as the identity
        token = flask_jwt_extended.create_access_token(identity=user["username"])
        return flask.jsonify({"message": "Login successful.", "token": token}), 200
    else:
        # If the passwords don't match, the login is invalid
        return flask.jsonify({"message": "Invalid username or password."}), 400


@api_v1_bp.route("/getuserinfo", methods=["GET"])
@flask_jwt_extended.jwt_required()
def get_user_info():
    """
    A route function to retrieve the account information for the authenticated user.

    Returns:
        A JSON object containing the account information for the authenticated user.
        The object has the following format:
        {
            "message": "Account information found.",
            "username": <username>,
            "email": <email>
        }
        If the authentication token is missing or invalid, or if the authenticated user is not found in the database,
        the function returns an error message as a JSON object with a corresponding HTTP status code.
    """
    # Get the authentication token from the Authorization header in the HTTP request
    auth_header = flask.request.headers.get("Authorization")
    if auth_header is None:
        # If the authentication header is missing, return an error message with HTTP status code 401 (Unauthorized)
        return flask.jsonify({"message": "Authorization header is missing."}), 401

    # Parse the authentication header and retrieve the JWT token from it
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        # If the authentication header is in the wrong format, return an error message with HTTP status code 401 (Unauthorized)
        return flask.jsonify({"message": "Invalid Authorization header format."}), 401
    token = parts[1]

    # Decode the JWT token to get the username of the authenticated user
    decoded_token = flask_jwt_extended.decode_token(token)
    username = decoded_token["sub"]

    db = get_db()

    # Retrieve the account information for the authenticated user from the database
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM "confirmed_users" WHERE username=?""", (username,))
    user_info = cursor.fetchone()
    cursor.close()

    if user_info is None:
        # If the authenticated user is not found in the database, return an error message with HTTP status code 404 (Not Found)
        return flask.jsonify({"message": "User not found."}), 404

    # If the account information is found, return it as a JSON object with HTTP status code 200 (OK)
    return flask.jsonify({"message": "Account information found.", "username": user_info["username"], "email": user_info["email"]}), 200

    
@api_v1_bp.route("/getblogs/<username>/<amount>", methods=["GET"])
def get_blogs(username, amount):
    """Fetches the specified number of blogs published by the given user.

    Args:
        username (str): The username of the user whose blogs should be fetched.
        amount (str): The number of blogs to fetch.

    Returns:
        A JSON response containing a message indicating success or failure, and either the requested blogs as a list
        of dictionaries (if successful), or an error message (if unsuccessful).
    """
    db = get_db()

    # Retrieve the user ID associated with the given username.
    cursor = db.cursor()
    cursor.execute("""SELECT "user_id" FROM "confirmed_users" WHERE username=?""", (username,))
    user_id = cursor.fetchone()
    cursor.close()
    
    # If no user was found, return an error message.
    if user_id is None:
        return flask.jsonify({
            "message": "User not found"
        }), 404
    else:
        user_id = user_id[0]

    # Retrieve the specified number of blogs published by the given user.
    cursor = db.cursor()
    cursor.execute("""SELECT blog_id, blog_title, unix_time FROM "blogs" WHERE user_id=? ORDER BY unix_time DESC""", (user_id,))
    rows = cursor.fetchmany(int(amount))
    cursor.close()
    
    if rows:
        # Get the column names from the cursor description
        columns = [column[0] for column in cursor.description]
        # Convert each row to a dictionary with column names as keys
        results = [dict(zip(columns, row)) for row in rows]
        # Return the requested blogs as a JSON response.
        return flask.jsonify({"message": "Blogs found.", "blogs": results}), 200
    else:
        # If no blogs were found, return an error message.
        return flask.jsonify({"message": "This user has no published blogs."}), 404

    
@api_v1_bp.route("/getblog/<username>/<blog_id>", methods=["GET"])
def get_blog(username, blog_id):
    """Retrieve a blog post by its ID for a given user.
    
    Args:
        username (str): The username of the user who published the blog post.
        blog_id (int): The ID of the blog post to retrieve.
        
    Returns:
        A JSON object with the retrieved blog post, including its title, content, and creation time, or a message indicating that the blog post was not found.
    """
    db = get_db()

    # Query the database to retrieve the user ID for the given username.
    cursor = db.cursor()
    cursor.execute("""SELECT "user_id" FROM "confirmed_users" WHERE username=?""", (username,))
    user_id = cursor.fetchone()
    cursor.close()
    
    # If the user is not found, return an error message.
    if user_id is None:
        return flask.jsonify({
            "message": "User not found"
        }), 404
    else:
        user_id = user_id[0]

    # Query the database to retrieve the blog post with the given ID and user ID.
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM "blogs" WHERE user_id=? AND blog_id=?""", (user_id, blog_id,))
    blog = cursor.fetchone()
    cursor.close()
    
    # If the blog post is found, return it as a JSON object.
    if blog:
        return flask.jsonify({
            "message": "Blog found.", 
            "blog_title": blog["blog_title"], 
            "blog_html": blog["blog_html"], 
            "unix_time": blog["unix_time"]
        }), 200
    else:
        # If the blog post is not found, return an error message.
        return flask.jsonify({"message": "Blog not found."}), 404


@api_v1_bp.route("/postblog", methods=["POST"])
def post_blog():
    """
    POST a new blog to the server, associated with the authenticated user.

    This function expects an HTTP POST request with a valid JSON payload containing a blog title and HTML content,
    along with a valid JWT token in the Authorization header. The payload should have the following format:

    {
        "blog_title": "The title of the blog",
        "blog_html": "The HTML content of the blog"
    }

    The function decodes the JWT token to retrieve the username of the authenticated user, and uses this username to
    retrieve the corresponding user ID from the database. If the user is not found, a 404 error is returned.

    The function then processes the blog HTML content, converting any base64-encoded images to URL references and
    saving the images to the server's file system.

    Finally, the function generates a new blog ID, inserts the blog metadata and HTML content into the database,
    and returns a success message with the ID of the new blog.

    Returns:
        A JSON response with the following format:
        {
            "message": "Blog posted.",
            "blog_id": "<id of the new blog>"
        }
        If the request is not authenticated or contains invalid credentials, or if there is an error inserting the
        blog data into the database, an error message is returned instead.

    """
    # This line gets the token from the Authorization header in the HTTP request.
    # The header value is expected to have the format "Bearer <token>".
    auth_header = flask.request.headers.get("Authorization")

    # Check if the Authorization header is present in the request
    if auth_header is None:
        return flask.jsonify({"message": "Authorization header is missing."}), 401
    
    # Check if the Authorization header has the correct format
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return flask.jsonify({"message": "Invalid Authorization header format."}), 401
    token = parts[1]

    # Decode the JWT token to get the username of the authenticated user.
    decoded_token = flask_jwt_extended.decode_token(token)
    username = decoded_token["sub"]

    # Connect to the database and get the user ID from the username
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT "user_id" FROM "confirmed_users" WHERE username=?""", (username,))
    user_id = cursor.fetchone()
    cursor.close()

    # If the user is not found, return a 404 error
    if user_id is None:
        return flask.jsonify({"message": "User not found"}), 404
    else:
        user_id = user_id[0]

    # Get the blog HTML and title from the POST request
    data = flask.request.get_json()
    blog_html = data["blog_html"]
    blog_title = data["blog_title"]
    unix_time = time.time()

    # Generate a unique ID for the blog and convert base64 images to URL images
    blog_id = get_unique_id()
    new_blog_html = str(blog_html)
    url_sources = []
    base64_sources = find_base64_sources(blog_html)
    for base64_str in base64_sources:
        # Generate a unique file name
        file_name = get_random_file_name(config["FILE_NAME_DIGIT_LENGTH"])
        # Save the base64 image to a file and replace the base64 string with the URL of the file
        file_url = save_base64_to_file(base64_str, file_name)
        new_blog_html = new_blog_html.replace(base64_str, file_url)

    # Insert the blog into the database and commit the transaction
    cursor = db.cursor()
    query = """INSERT INTO "blogs" (blog_id, user_id, blog_title, blog_html, unix_time) VALUES (?, ?, ?, ?, ?)"""
    values = (blog_id, user_id, blog_title, new_blog_html, unix_time,)
    cursor.execute(query, values)
    cursor.close()
    db.commit()

    # Return a success message with the ID of the posted blog
    return flask.jsonify({"message": "Blog posted.", "blog_id": blog_id}), 200


@api_v1_bp.route("/usercontent/<file_name_with_extension>", methods=["GET"])
def serve_usercontent(file_name_with_extension):
    """
    Serve a file from the usercontent directory.

    Args:
        file_name (str): The name of the file to serve.

    Returns:
        flask.Response: The HTTP response containing the file, or a JSON error message if the file is not found.
    """
    
    file_name_with_extension = str(file_name_with_extension)

    extension_dot_index = file_name_with_extension.find(".")
    if extension_dot_index == -1:
        return flask.jsonify({
            "message": "File name does not have an extension."
        }), 400
    file_name = file_name_with_extension[:extension_dot_index]

    file_name_digit_length = config["FILE_NAME_DIGIT_LENGTH"]
    if not file_name.isdigit() or len(file_name) != file_name_digit_length:
        return flask.jsonify({
            "message": "Invalid file name."
        }), 400

    # Get the full path to the file
    folder_path = os.path.join(os.getcwd(), config["USERCONTENT_FOLDER"])
    file_path = os.path.join(folder_path, file_name_with_extension)

    print(file_path)

    # Check if the file exists
    if not os.path.isfile(file_path):
        return flask.jsonify({
            "message": "File not found."
        }), 404

    # Serve the file
    return flask.send_from_directory(folder_path, file_name_with_extension)


@api_v1_bp.route("/operation/create", methods=["POST"])
@flask_jwt_extended.jwt_required()
def create_operation():
    """
    Creates a new operation for a user, sends an email confirmation with links to run or cancel the operation,
    and saves the operation data to the database.
    
    Returns:
        A JSON object containing a message about the email confirmation and a status code of 200 on success.
        A JSON object containing an error message and a status code of 401 or 404 on failure.
    Raises:
        None
    Args:
        None
    """

    # Get the authorization header from the request and extract the JWT token
    auth_header = flask.request.headers.get("Authorization")
    if auth_header is None:
        return flask.jsonify({
            "message": "Authorization header is missing."
        }), 401

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return flask.jsonify({
            "message": "Invalid Authorization header format."
        }), 401
    
    token = parts[1]
    decoded_token = flask_jwt_extended.decode_token(token)
    username = decoded_token["sub"]

    # Get the operation data from the request
    data = flask.request.get_json()
    operation = data["operation"]
    operation_value = data["operation_value"]
    operation_id = get_unique_id()
    
    db = get_db()

    # Get the user ID from the database using the username
    cursor = db.cursor()
    cursor.execute("""SELECT "user_id" FROM "confirmed_users" WHERE username=?""", (username,))
    user_id = cursor.fetchone()
    cursor.close()
    
    if user_id is None:
        return flask.jsonify({
            "message": "User not found"
        }), 404
    else:
        user_id = user_id[0]

    # If the operation is a password change, hash the new password using the user's salt and peppers
    if operation == "password":
        query = """
            SELECT salt FROM "confirmed_users"
            WHERE ("username" = ?)
        """
        values = (username,)

        cursor = db.cursor()
        cursor.execute(query, values)
        salt = cursor.fetchone()
        cursor.close()

        if salt is None:
            return flask.jsonify({
                "message": "User not found"
            }), 404
        else:
            salt = salt[0]
            
        _, operation_value = hash_salt_pepper(
            operation_value, 
            peppers=config["PEPPERS"], 
            salt=salt
        )

    # Generate URLs for the run and cancel endpoints
    run_operation_url = flask.url_for(
        "api_v1.run_operation", 
        user_id=user_id, 
        operation=operation, 
        operation_id=operation_id, 
        _external=True
    )
    cancel_operation_url = flask.url_for(
        "api_v1.cancel_operation", 
        user_id=user_id, 
        operation=operation, 
        operation_id=operation_id, 
        _external=True
    )

    # Get the user's email address from the database
    query = """
        SELECT email FROM "confirmed_users"
        WHERE ("username" = ?)
    """
    values = (username,)
    cursor = db.cursor()
    cursor.execute(query, values)
    email = cursor.fetchone()
    cursor.close()
        
    if email is None:
        return flask.jsonify({
            "message": "User not found"
        }), 404
    else:
        email = email[0]

    # Send the confirmation email to the user
    msg = flask_mail.Message()
    msg.subject = config["OPERATION_EMAIL_SUBJECT"]
    msg.html = config["OPERATION_EMAIL_BODY"] \
        .replace("««««USERNAME»»»»", username) \
        .replace("««««OPERATION»»»»", operation) \
        .replace("««««RUN_OPERATION_URL»»»»", run_operation_url) \
        .replace("««««CANCEL_OPERATION_URL»»»»", cancel_operation_url)
    msg.recipients = [email]
    mail.send(msg)

    query = """
        INSERT INTO "operations"
        ("operation_id", "operation", "user_id", "operation_value")
        VALUES (?, ?, ?, ?)
    """
    values = (operation_id, operation, user_id, operation_value)
    cursor = db.cursor()
    cursor.execute(query, values)
    cursor.close()
    db.commit()

    return flask.jsonify({
        "message": "Email confirmation sent, check your email (If you can't find it, look in the spam folder)."
    }), 200


@api_v1_bp.route("/operation/cancel/<user_id>/<operation>/<operation_id>", methods=["GET"])
def cancel_operation(user_id, operation, operation_id):
    """
    Cancel a previously requested operation.

    Args:
        user_id (str): The ID of the user requesting to cancel the operation.
        operation (str): The name of the operation to cancel.
        operation_id (str): The unique ID of the operation to cancel.

    Returns:
        A JSON response containing a message indicating whether the operation was successfully canceled or not.
    """
    # Construct a DELETE query to remove the operation from the database.
    query = """
        DELETE FROM "operations"
        WHERE ("user_id" = ?)
        AND ("operation" = ?) 
        AND ("operation_id" = ?)
    """
    values = (user_id, operation, operation_id)
    
    db = get_db()

    # Execute the query and get the number of rows deleted.
    cursor = db.cursor()
    cursor.execute(query, values)
    deleted_rows = cursor.rowcount
    cursor.close()
    db.commit()

    # If no rows were deleted, the operation ID was not found.
    if deleted_rows <= 0:
        return flask.jsonify(
            {"message": "Operation ID not found."}
        ), 400

    # Otherwise, the operation was successfully canceled.
    else:
        return flask.jsonify(
            {"message": "Operation canceled"}
        ), 200


@api_v1_bp.route("/operation/run/<user_id>/<operation>/<operation_id>", methods=["GET"])
def run_operation(user_id, operation, operation_id):
    db = get_db()

    query = """
        SELECT * FROM "operations" 
        WHERE ("user_id" = ?) 
        AND ("operation" = ?) 
        AND ("operation_id" = ?)
    """
    values = (user_id, operation, operation_id)
    cursor = db.cursor()
    cursor.execute(query, values)
    operation_info = cursor.fetchone()
    cursor.close()
        
    if operation_info is None:
        return flask.jsonify({
            "message": "Operation not found"
        }), 404
    else:
        operation_value = operation_info["operation_value"]

    if not operation:
        return flask.jsonify({
            "message": "Operation not found!"
        }), 404

    operation_successful = False

    if operation == "email":
        email = operation_value
        query = """
            UPDATE "confirmed_users"
            SET "email" = ?
            WHERE "user_id" = ?
        """
        values = (email, user_id)
        cursor = db.cursor()
        cursor.execute(query, values)
        operation_successful = cursor.rowcount > 0
        cursor.close()
        db.commit()

    elif operation == "username":
        new_username = operation_value
        query_1 = """
            UPDATE "confirmed_users"
            SET "username" = ?
            WHERE "user_id" = ?
        """
        values = (new_username, user_id)
        cursor = db.cursor()
        cursor.execute(query_1, values)
        operation_successful = cursor.rowcount > 0
        cursor.close()
        query_2 = """
            SELECT COUNT(*) FROM "blogs"
            WHERE "user_id" = ?
        """
        values = (user_id,)
        cursor = db.cursor()
        cursor.execute(query_2, values)
        count = cursor.fetchone()[0] 
        cursor.close()
        db.commit()

    elif operation == "password":
        new_password = operation_value
        query = """
            UPDATE "confirmed_users"
            SET "password" = ?
            WHERE "user_id" = ?
        """
        values = (new_password, user_id)
        cursor = db.cursor()
        cursor.execute(query, values)
        operation_successful = cursor.rowcount > 0
        cursor.close()
        db.commit()
    
    elif operation == "delete":
        query_1 = """
            DELETE FROM "confirmed_users"
            WHERE "user_id" = ?
        """
        values = (user_id,)
        cursor = db.cursor()
        cursor.execute(query_1, values)
        operation_successful = cursor.rowcount > 0
        cursor.close()
        query_2 = """
            SELECT COUNT(*) FROM "blogs"
            WHERE "user_id" = ?
        """
        values = (user_id,)
        cursor = db.cursor()
        cursor.execute(query_2, values)
        count = cursor.fetchone()[0]
        if count > 0:
            query_3 = """
                DELETE FROM "blogs"
                WHERE "user_id" = ?
            """
            values = (user_id,)
            cursor.execute(query_3, values)
            operation_successful = cursor.rowcount > 0 and operation_successful
        cursor.close()
        db.commit()

    else:
        return flask.jsonify({
            "message": f"""Invalid operation: {operation["operation"]}"""
        }), 400

    if not operation_successful:
        return flask.jsonify({
            "message": "Operation did not succeed!"
        }), 500


    query = """
        DELETE FROM "operations"
        WHERE "operation_id" = ?
        AND "operation" = ?
        AND "user_id" = ?
    """
    values = (operation_id, operation, user_id)
    cursor = db.cursor()
    cursor.execute(query, values)
    operation_deletion_successful = cursor.rowcount > 0
    cursor.close()

    db.commit()
    
    if not operation_deletion_successful:
        return flask.jsonify({
            "message": "Operation didn't finish correctly"
        }), 500

    return flask.jsonify({
        "message": "Operation executed successfully"
    }), 200


# Register the blueprint
app.register_blueprint(api_v1_bp)

with app.app_context():
    create_tables()
    create_usercontent_folder()
