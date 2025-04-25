import uuid,os,base64
from werkzeug.security import check_password_hash,generate_password_hash
from werkzeug.utils import secure_filename

image_path = os.path.join('static', 'files','img')
videos_path = os.path.join('static', 'files','videos')
import mysql.connector

try:


    mydb = mysql.connector.connect(
    host="localhost",        # MySQL server is running locally
    user="root",             # Username for connecting to the database
    password="5000",         # Password for the MySQL user 'root'
    database="homemade_easier"  # Database you want to connect to
    )

    mycursor = mydb.cursor()


except Exception as err:
    print(err)    

def createNewUser(Userinfo):
    if Userinfo:
        id = Userinfo.get('id',None)
        name = Userinfo['name']
        password = Userinfo.get('password', None)
        email = Userinfo['email']
        profilePicture = Userinfo.get('picture', None)  # Use .get() for optional fields
        phone_number = Userinfo.get('phone_number', None)

        if not id:
            id = str(uuid.uuid4())  

        
        # Hash the password if it's provided
        if password:
            password = generate_password_hash(password)

        filename = None   
        if profilePicture:
            if isinstance(profilePicture, str) and profilePicture.startswith("data:image"): 
                try:
                    image_data = profilePicture.split(",")[1]  # Extract image data without prefix
                    filename = f"user_{image_data[3]}.png"  
                    picture_path = os.path.join(image_path, filename)

                    with open(picture_path, "wb") as img_file:
                        img_file.write(base64.b64decode(image_data))

                except Exception as e:
                    return {"success": False, "message": f"Failed to process image: {str(e)}"}

            elif hasattr(profilePicture, "filename"):  
                filename = secure_filename(f"user_{image_data[3]}.png") 
                picture_path = os.path.join(image_path, filename)

                profilePicture.save(picture_path)




        try:
            mycursor.execute(
                "INSERT INTO client (email, name, password, picture,phonenumber) VALUES (%s, %s, %s, %s,%s)",
                (email, name,password , filename, phone_number)
            )
            mydb.commit()  # Commit the transaction
            return True
        except Exception as err:
            print("Error: %s", err) 
            return str(err)
    return False



def update_UserProfile(userId, username=None, email=None, password=None, phone=None,location=None):
    if not userId:
        return {"success": False, "message": "User ID is required."}

    update_query = []
    params = []

    if username:
        update_query.append("name=%s")
        params.append(username)

    if email:
        update_query.append("email=%s")
        params.append(email)

    if phone:
        update_query.append("phonenumber=%s")
        params.append(phone)

    if password:
        password_hashed = generate_password_hash(password)
        update_query.append("password=%s")
        params.append(password_hashed)    



    if not update_query:
        return {"success": False, "message": "No updates provided."}

    update_query_str = ", ".join(update_query)
    params.append(userId)

    sql_query = f"UPDATE client SET {update_query_str} WHERE clientid=%s"

    print("Updating profile:", update_query_str)

    try:
        mycursor.execute(sql_query, tuple(params))
        mydb.commit()
        return {"success": True, "message": "Profile updated successfully."}
    except mysql.connector.Error as err:
        print(f"Error updating user profile: {err}")
        return {"success": False, "message": "Failed to update profile."}



def fetch_user(user_id):
    if not user_id:
        return {
            "success": False,
            "message": "User ID is required"
        }

    if '@' in user_id and '.' in user_id:
        select = 'email'
    else:
        select = 'id'

    try:
        query = f"SELECT * FROM client WHERE {select} = %s"
        mycursor.execute(query, (user_id,))
        user = mycursor.fetchone()

        if user:
            return {
                'success': True,
                "id": user[1],
                "email": user[0],
                "name": user[2],
                "picture": user[3],
                "phonenumber": user[4],
                "created_at": user[6]
            }
        else:
            return {
                'success': False,
                "message": "User not found"
            }
    except Exception as err:
        print("Error: %s", err)
        return {"success": False, "error": "An unexpected error occurred"}



def validate_user_login(email, password):
    try:
        print(f"Querying user with email: {email}")  # Debugging line to check email being queried

        
        mycursor.execute(
            "SELECT email, password, name, picture, clientid, phonenumber FROM client WHERE email = %s",
            (email,)
        )
        user = mycursor.fetchone()

        if user is None:
            return {"userFound": False}

        db_email, db_password, db_name, db_picture, db_id, db_phonenumber = user

        # Debugging line to confirm if data was fetched correctly
        print(f"User found: {db_email}, {db_name}, {db_phonenumber}")  

        # Compare hashed password
        if check_password_hash(db_password, password):
            user_info = {
                "email": db_email,
                "id": db_id,
                "name": db_name,
                "picture":f"{image_path}/{db_picture}",
                "phonenumber": db_phonenumber
            }
            print('Password Matched!')  # Debugging line to confirm password match

            return {"user_info": user_info, "userFound": True, "truepassword": True}

        return {"user_info": None, "userFound": True, "truepassword": False}
    except Exception as err:
        print(f"Error validating user login: {err}")  # Enhanced error message
        return {"error": f"An error occurred during login validation: {str(err)}"}


