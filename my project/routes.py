@auth_login_bp.route('/login/email', methods=['POST'])
def email_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')


        if not email or not password:
            return jsonify(success=False, message="Email and password are required."), 400

        result = validate_user_login(email, password)

        if not result:
            return jsonify(success=False, message="An error occurred during login."), 500

        if not result.get('userFound'):
            return jsonify(success=False, message="User not found. Please check your email or sign up!"), 404

        if not result.get('truepassword'):
            return jsonify(success=False, message="Incorrect password. Please try again!"), 400

        if result.get('user_info'):
            user_info = result['user_info']
            print("User info::💯", user_info)
            session['user_info'] = user_info
            return jsonify(success=True, message="success"), 200


            #return redirect(url_for('main.user_index', user_email=email))

        return jsonify(success=False, message="Unexpected error during login."), 500

    except Exception as e:
        logging.error("Error during email login: %s", e)
        return jsonify(success=False, message="Internal server error. Please try again later."), 500



@user_bp.route('/create', methods=['POST'])
def create_user():
    data = request.json
    
    # Validate the input JSON
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    # Default profile picture
    profile = data.get('picture', 'static/img/icon3.jpg')

    # Ensure all required fields are provided
    if not email or not name or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Validate email format
    if '@' not in email:
        return jsonify({
            'error': 'Invalid email format',
            'msg_type': 'ERROR'
        }), 400

    # Validate password length
    if len(password) < 8:
        return jsonify({
            'error': 'Password must be at least 8 characters long',
            'msg_type': 'ERROR'
        }), 400
    # Check if user already exists (validate_user function should be implemented)
    if validate_user(email):
        return jsonify({
            'error': 'Email already exists Kindly Login or reset password',
            'msg_type': 'ERROR'
        }), 400

    # Construct the user information
    user_info = {
        "email": email,
        "family_name": "",
        "given_name": "",
        "id": "",  # Generate a unique user ID here if necessary
        "name": name,
        "password": password,  # Hash the password before storing it
        "picture": profile,
        "verified_email": False
    }

    # Send verification link (send_verify_link function should be implemented)
    result = send_verify_link(email)
    if result['success'] == False:
        return jsonify({
            'error': 'Failed to send verification email. Please try again later.',
            'msg_type': 'ERROR'
        }), 500

    # Create new user (createNewUser function should be implemented)
    createNewUser(user_info)
    
    return jsonify({
        'error': None,
        'msg_type': 'SUCCESS',
        'message': result['message'],
        'data': {
            'email': email,
            'name': name
        }
    }), 200
@user_bp.route("/updateProfile", methods=["POST"])
def updateProfile():
    try:
        userId = request.form.get('userId')

        if not userId:
            return jsonify({"success": False, "message": "You need to log in!"})

        email = request.form.get('email', None)
        name = request.form.get('name', None)
        password = request.form.get('password', None)
        profilePic = request.files.get('newPicture') or request.form.get('newPicture')

        print("Updating profile....")
        result = update_UserProfile(userId, name, email, password, profilePic)  # ✅ Pass raw image

        if result.get('success'):
            return jsonify({"success": True, "message": "Profile updated successfully."})
        else:
            return jsonify({"success": False, "message": "Failed to update profile."})

    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)})

def validate_user(user_email):
    try:
        mycursor.execute("SELECT verified_email FROM injustifyUsers WHERE email = %s", (user_email,))
        user = mycursor.fetchone()
        if user and user[0] == 1:
            return True
        else:
            return False
    except Exception as err:
        logging.error("Error: %s", err)
        return False
def createNewUser(Userinfo):
    if Userinfo:
        id = Userinfo.get('id',None)
        name = Userinfo['name']
        password = Userinfo.get('password', None)
        email = Userinfo['email']
        profilePicture = Userinfo.get('picture', None)  # Use .get() for optional fields
        verified_email = Userinfo.get('verified_email', False)

        if not id:
            id = str(uuid.uuid4())  

        
        # Hash the password if it's provided
        if password:
            password = generate_password_hash(password)

        if not profilePicture:
            profilePicture ='static/img/icon3.jpg'  # Default profile picture


        try:
            mycursor.execute(
                "INSERT INTO injustifyUsers (id,email, name, password, picture,verified_email) VALUES (%s,%s, %s, %s, %s,%s)",
                (id,email, name,password , profilePicture, verified_email)
            )
            mydb.commit()  # Commit the transaction
            return 'success'
        except Exception as err:
            logging.error("Error: %s", err) 
            return str(err)
    return 'error'

