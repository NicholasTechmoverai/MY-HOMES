from flask import Flask, jsonify, request,render_template,session
from datetime import datetime
# import flask-socketio
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = "5000"
import os
image_path = os.path.join('static', 'files','img')
videos_path = os.path.join('static', 'files','videos')

from hlp import validate_user_login,fetch_user,update_UserProfile,createNewUser

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



@app.route('/login/email', methods=['POST'])
def email_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        print(f"Email received: {email}")  # Debugging line to check the received email

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
            user_info = result.get('user_info')
            print("User info::💯", user_info)  # Debugging line to check user info

            session['user_info'] = user_info
            return jsonify(success=True, message="success",user_info=user_info), 200

        return jsonify(success=False, message="Unexpected error during login."), 500

    except Exception as e:
        print(f"Error during email login: {e}")  # Debugging error on the route
        return jsonify(success=False, message="Internal server error. Please try again later."), 500



@app.route('/logout', methods=['GET'])
def logout_route():
    """
    Log the user out and clear the session.
    """
    session.clear()  # Clear session
    return render_template('index.html')#redirect(url_for('main.noindexx'))  # Redirect to guest route after logout


@app.route('/create', methods=['POST'])
def create_user():
    data = request.json
    
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    phone_number = data.get('phone_number')

    print(email,name,password,phone_number)

    profile = data.get('picture',None)

    # Ensure all required fields are provided
    if not email or not name or not password or not phone_number:
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
        "name": name,
        "password": password,  # Hash the password before storing it
        "picture": profile,
        "phone_number": phone_number
    }

    result = createNewUser(user_info)

    if result:
        return jsonify({
            'error': None,
            'msg_type': 'SUCCESS',
            'message': 'acoount created successfully',
            'data': {
                'email': email,
                'name': name
            }
        }), 200
    else:
        return jsonify({
            'error': "Error creating account",
            'msg_type': 'error',
            'message': "Error creating account" ,
            'data': {
                'email': email,
                'name': name
            }
        }), 200

@app.route("/updateProfile", methods=["POST"])
def updateProfile():
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        userId = data.get('user_id')
        if not userId:
            return jsonify({"success": False, "message": "User ID is required"}), 400

        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        location = data.get('location')
        password = data.get('password')

       

        print(f"Updating profile for user {userId}...")
        result = update_UserProfile(
            userId=userId,
            username=name,
            email=email,
            phone=phone,
            password=password,
            location=location
        )

        if result.get('success'):
            return jsonify({
                "success": True,
                "message": "Profile updated successfully",
                "user_info": result.get('user_info', {})
            })
        else:
            return jsonify({
                "success": False,
                "message": result.get('message', "Failed to update profile")
            }), 400

    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while updating profile",
            "error": str(e)
        }), 500
    
def validate_user(user_email):
    try:
        mycursor.execute("SELECT * FROM client WHERE email = %s", (user_email,))
        user = mycursor.fetchone()
        if user :
            return True
        else:
            return False
    except Exception as err:
        print("Error: %s", err)
        return False
    


# Configure upload folder
UPLOAD_FOLDER = image_path
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/submit-property', methods=['POST'])
def submit_property():
    # Basic validation for required fields
    required_fields = ['title', 'type', 'address', 'city', 'price', 'size', 
                      'bedrooms', 'bathrooms', 'description', 'contact_name',
                      'contact_phone', 'contact_email','owner_id']
    
    for field in required_fields:
        if not request.form.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    try:
      
        owner_id = request.form['owner_id']

        # Insert property data
        property_data = {
            'owner_id': owner_id,
            'title': request.form['title'],
            'description': request.form['description'],
            'price': float(request.form['price']),
            'address': request.form['address'],
            'city': request.form['city'],
            'property_type': request.form['type'],
            'size_sqft': int(request.form['size']),
            'bedrooms': int(request.form['bedrooms']),
            'bathrooms': int(request.form['bathrooms']),
            'year_built': int(request.form['year']) if request.form.get('year') else None,
            'contact_name': request.form['contact_name'],
            'contact_phone': request.form['contact_phone'],
            'contact_email': request.form['contact_email']
        }

        insert_property = """
            INSERT INTO property (
                owner_id, title, description, price, address, city, property_type,
                size_sqft, bedrooms, bathrooms, year_built, contact_name, contact_phone, contact_email
            ) VALUES (
                %(owner_id)s, %(title)s, %(description)s, %(price)s, %(address)s, %(city)s, %(property_type)s,
                %(size_sqft)s, %(bedrooms)s, %(bathrooms)s, %(year_built)s, %(contact_name)s, %(contact_phone)s, %(contact_email)s
            )
        """
        
        mycursor.execute(insert_property, property_data)
        property_id = mycursor.lastrowid

        # Handle amenities
        amenities = request.form.getlist('amenities')
        if amenities:
            amenity_values = [(property_id, amenity) for amenity in amenities]
            mycursor.executemany(
                "INSERT INTO property_amenities (property_id, amenity) VALUES (%s, %s)",
                amenity_values
            )

        # # Handle file uploads
        # if 'images' not in request.files:
        #     return jsonify({'error': 'No images uploaded'}), 400
            
        # files = request.files.getlist('images')
        
        # if len(files) < 3:
        #     mydb.rollback()
        #     return jsonify({'error': 'Minimum 3 images required'}), 400
            
        # if len(files) > 10:
        #     mydb.rollback()
        #     return jsonify({'error': 'Maximum 10 images allowed'}), 400
        files = request.files.getlist('images[]')  # match name="images[]"
       
        for i, file in enumerate(files):
            if file and allowed_file(file.filename):
                # filename = secure_filename(file.filename)
                filename = secure_filename(f"{property_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}.{file.filename.rsplit('.', 1)[1].lower()}")

                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                # Store relative path in database
                is_featured = 1 if i == 0 else 0  # First image is featured
                
                mycursor.execute(
                    "INSERT INTO property_images (property_id, image_path, is_featured) VALUES (%s, %s, %s)",
                    (property_id, filename, is_featured)
                )
            else:
                mydb.rollback()
                return jsonify({'error': 'Invalid file type'}), 400

        mydb.commit()
        return jsonify({
            'success': True,
            'message': 'Property listed successfully',
            'property_id': property_id,
        }), 201

    except Exception as e:
        mydb.rollback()
        print(f"Error submitting property: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500



@app.route('/property/<int:id>', methods=['GET'])
def get_property_by_id(id):
    try:
        # Query to fetch a single property by ID
        query = """
            SELECT 
                p.property_id, p.title, p.description, p.price, 
                p.address, p.city, p.property_type, p.size_sqft,
                p.bedrooms, p.bathrooms, p.year_built, p.listing_date,
                p.contact_name, p.contact_phone, p.contact_email,
                c.name AS owner_name, c.email AS owner_email, c.phonenumber AS owner_phonenumber,
                c.picture AS owner_picture
            FROM property p
            JOIN client c ON p.owner_id = c.clientid
            WHERE p.property_id = %s
        """
        mycursor.execute(query, (id,))
        prop = mycursor.fetchone()

        if not prop:
            return "Property not found", 404

        # Fetch amenities
        mycursor.execute("""
            SELECT amenity FROM property_amenities WHERE property_id = %s
        """, (id,))
        amenities = [row[0] for row in mycursor.fetchall()]

        # Fetch images
        mycursor.execute("""
            SELECT image_path, is_featured
            FROM property_images
            WHERE property_id = %s
            ORDER BY is_featured DESC, upload_date DESC
        """, (id,))
        images = [{
            'url': f"/{image_path}/{row[0]}",
            'is_featured': bool(row[1])
        } for row in mycursor.fetchall()]

        featured_image = next((img['url'] for img in images if img['is_featured']), images[0]['url'] if images else None)

        # Build details dictionary
        property_data = {
            'property_id': prop[0],
            'title': prop[1],
            'description': prop[2],
            'price': float(prop[3]),
            'address': prop[4],
            'city': prop[5],
            'property_type': prop[6],
            'size_sqft': prop[7],
            'bedrooms': prop[8],
            'bathrooms': prop[9],
            'year_built': prop[10],
            'listing_date': prop[11].isoformat() if prop[11] else None,
            'contact_info': {
                'name': prop[12],
                'phone': prop[13],
                'email': prop[14]
            },
            'owner_info': {
                'name': prop[15],
                'email': prop[16],
                'phone': prop[17],
                'picture': prop[18] if 'https://' in prop[18] else f'/{image_path}/{prop[18]}'
            },
            'amenities': amenities,
            'images': images,
            'featured_image': featured_image
        }

        # Render the template with property details
        return render_template('indetails.html', details=property_data)

    except Exception as e:
        import traceback
        app.logger.error(f"Error fetching single property: {str(e)}\n{traceback.format_exc()}")
        return "Server Error", 500

@app.route('/fetchproperties_special', methods=['POST'])
def load_properties_special():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data received'}), 400

        # Extract filters from request
        sale_type = data.get('type')  # 'rent', 'sale', or None
        property_type = data.get('property_type')  # 'house', 'apartment', 'land', 'commercial'
        city = data.get('city')
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        bedrooms = data.get('bedrooms')
        bathrooms = data.get('bathrooms')
        min_year = data.get('min_year_built')
        max_year = data.get('max_year_built')
        property_id = data.get('property_id')
        owner_id = data.get('owner_id')


        limit = min(int(data.get('limit', 20)), 100)
        offset = int(data.get('offset', 0))

        # Build query
        base_query = """
            SELECT 
                p.property_id, p.title, p.description, p.price, 
                p.address, p.city, p.property_type, p.size_sqft,
                p.bedrooms, p.bathrooms, p.year_built, p.listing_date,
                p.contact_name, p.contact_phone, p.contact_email,
                c.name AS owner_name, c.email AS owner_email, c.phonenumber AS owner_phonenumber,
                c.picture AS owner_picture
            FROM property p
            JOIN client c ON p.owner_id = c.clientid
        """

        conditions = []
        params = []

        # Apply filters
        if property_id:
            conditions.append("p.property_id = %s")
            params.append(property_id)

        if owner_id:
            conditions.append("p.owner_id = %s")
            params.append(owner_id)

        if sale_type == 'rent':
            conditions.append("p.is_for_sale = 0")
        elif sale_type == 'sale':
            conditions.append("p.is_for_sale = 1")

        if property_type:
            conditions.append("p.property_type = %s")
            params.append(property_type)

        if city:
            conditions.append("p.city = %s")
            params.append(city)

        if min_price is not None:
            conditions.append("p.price >= %s")
            params.append(min_price)

        if max_price is not None:
            conditions.append("p.price <= %s")
            params.append(max_price)

        if bedrooms is not None:
            conditions.append("p.bedrooms = %s")
            params.append(bedrooms)

        if bathrooms is not None:
            conditions.append("p.bathrooms = %s")
            params.append(bathrooms)

        if min_year is not None:
            conditions.append("p.year_built >= %s")
            params.append(min_year)

        if max_year is not None:
            conditions.append("p.year_built <= %s")
            params.append(max_year)

        # Finalize query
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query += " ORDER BY p.listing_date DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        mycursor.execute(base_query, params)
        properties = mycursor.fetchall()

        if not properties:
            return jsonify({'success': True, 'properties': [], 'count': 0})

        property_ids = [str(prop[0]) for prop in properties]

        # Batch amenities
        amenity_query = f"""
            SELECT property_id, GROUP_CONCAT(amenity) AS amenities
            FROM property_amenities
            WHERE property_id IN ({','.join(['%s'] * len(property_ids))})
            GROUP BY property_id
        """
        mycursor.execute(amenity_query, property_ids)
        amenities_map = {row[0]: row[1].split(',') if row[1] else [] for row in mycursor.fetchall()}

        # Batch images
        image_query = f"""
            SELECT property_id, image_path, is_featured
            FROM property_images
            WHERE property_id IN ({','.join(['%s'] * len(property_ids))})
            ORDER BY is_featured DESC, upload_date DESC
        """
        mycursor.execute(image_query, property_ids)
        images_map = {}
        for row in mycursor.fetchall():
            if row[0] not in images_map:
                images_map[row[0]] = []
            images_map[row[0]].append({
                'url':f"{image_path}/{row[1]}",
                'is_featured': bool(row[2])
            })

        # Build response
        properties_list = []
        for prop in properties:
            pid = prop[0]
            featured_image = next(
                (img['url'] for img in images_map.get(pid, []) if img['is_featured']),
                images_map.get(pid, [{}])[0].get('url', None)
            )

            properties_list.append({
                'property_id': pid,
                'title': prop[1],
                'description': prop[2],
                'price': float(prop[3]),
                'address': prop[4],
                'city': prop[5],
                'property_type': prop[6],
                'size_sqft': prop[7],
                'bedrooms': prop[8],
                'bathrooms': prop[9],
                'year_built': prop[10],
                'listing_date': prop[11].isoformat() if prop[11] else None,
                'is_for_rent': sale_type == 'rent',
                'contact_info': {
                    'name': prop[12],
                    'phone': prop[13],
                    'email': prop[14]
                },
                'owner_info': {
                    'name': prop[15],
                    'email': prop[16],
                    'phone': prop[17],
                    'picture': prop[18]
                },
                'amenities': amenities_map.get(pid, []),
                'images': images_map.get(pid, []),
                'featured_image': featured_image
            })

        # Count for pagination
        count_query = "SELECT COUNT(*) FROM property p"
        if conditions:
            count_query += " WHERE " + " AND ".join(conditions)
        mycursor.execute(count_query, params[:-2])  # Remove limit/offset for count
        total_count = mycursor.fetchone()[0]

        return jsonify({
            'success': True,
            'properties': properties_list,
            'meta': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'returned': len(properties_list)
            }
        })

    except Exception as e:
        import traceback
        app.logger.error(f"Error fetching properties: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500



@app.route('/fetchvideos', methods=['POST'])
def load_videos():
    data = request.get_json()
    query = data.get('query', '')
    query = query.strip() if query else ''


    try:
        if not query or query.lower() == "null":
            # Fetch all videos
            mycursor.execute("""
                SELECT v.id, v.title, v.description, v.file_path, v.upload_date,
                       u.name AS uploader_name, u.email AS uploader_email, u.clientid
                FROM videos v
                LEFT JOIN client u ON v.uploaded_by = u.clientid
                ORDER BY v.upload_date DESC
            """)
            videos = mycursor.fetchall()
        else:
            search_term = f"%{query}%"
            mycursor.execute("""
                SELECT v.id, v.title, v.description, v.file_path, v.upload_date,
                       u.name AS uploader_name, u.email AS uploader_email, u.clientid
                FROM videos v
                LEFT JOIN client u ON v.uploaded_by = u.clientid
                WHERE v.title LIKE %s OR v.description LIKE %s
                ORDER BY v.upload_date DESC
            """, (search_term, search_term))
            videos = mycursor.fetchall()

        video_list = []

        for video in videos:
            video_id = video[0]

            # Likes
            mycursor.execute("SELECT COUNT(*) FROM likes WHERE video_id = %s", (video_id,))
            likes_count = mycursor.fetchone()[0]

            # Comments
            mycursor.execute("""
                SELECT c.comment_text, c.commented_at, u.name
                FROM comments c
                JOIN client u ON c.user_id = u.clientid
                WHERE c.video_id = %s
                ORDER BY c.commented_at DESC
            """, (video_id,))
            comments = mycursor.fetchall()

            comment_list = [
                {
                    'text': c[0],
                    'timestamp': c[1].strftime('%Y-%m-%d %H:%M:%S'),
                    'author': c[2]
                } for c in comments
            ]

            # Final video object
            video_info = {
                'video_id': video[0],
                'title': video[1],
                'description': video[2],
                'video_url': f"{videos_path}/{video[3]}",
                'upload_date': video[4].strftime('%Y-%m-%d %H:%M:%S'),
                'uploader_name': video[5],
                'uploader_email': video[6],
                'uploader_id': video[7],
                'likes': likes_count,
                'comments': comment_list
            }

            video_list.append(video_info)

        return jsonify({'success': True, 'videos': video_list})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})




@app.route('/like', methods=['POST'])
def like_video():
    data = request.get_json()
    user_id = data.get('user_id')
    video_id = data.get('video_id')
    column = 'user_id'
    
    if '@' in str(user_id):
        column = 'email'

    try:
        # Build SQL with column name directly
        sql = f"INSERT INTO likes ({column}, video_id) VALUES (%s, %s)"
        mycursor.execute(sql, (user_id, video_id))
        mydb.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/unlike', methods=['POST'])
def unlike_video():
    data = request.get_json()
    user_id = data.get('user_id')
    video_id = data.get('video_id')
    column = 'user_id'
    
    if '@' in str(user_id):
        column = 'email'

    try:
        # Build SQL with column name directly
        sql = f"DELETE FROM likes WHERE {column} = %s AND video_id = %s"
        mycursor.execute(sql, (user_id, video_id))
        mydb.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/post_comment', methods=['POST'])
def post_comment():
    data = request.get_json()
    user_id = data.get('user_id')
    video_id = data.get('video_id')
    comment = data.get('comment')
    try:
        mycursor.execute("INSERT INTO comments (user_id, video_id, comment_text) VALUES (%s, %s, %s)",
                         (user_id, video_id, comment))
        mydb.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})





@app.route('/update/image', methods=['POST'])
def upload_profile_image():
    # Check if file exists in request
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    
    file = request.files['file']
    user_id = request.form.get('user_id')
    
    # Validate inputs
    if not user_id:
        return jsonify({'success': False, 'error': 'User ID missing'}), 400
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Create secure filename
            ext = file.filename.rsplit('.', 1)[1].lower()
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"user_{user_id}_{timestamp}.{ext}"
            filename = secure_filename(filename)
            

            # Save file
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Update database (relative path for web access)
            web_path = f"{filename}"
            mycursor.execute("""
                UPDATE client
                SET picture = %s
                WHERE clientid = %s
            """, (web_path, user_id))
            
            mydb.commit()
            
            return jsonify({
                'success': True,
                'message': 'Image updated successfully',
                'image_path': web_path,
                'user_info': {
                    # Include any updated user info you want to return
                    'id': user_id,
                    'picture': web_path
                }
            })
            
        except Exception as e:
            mydb.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return jsonify({'success': False, 'error': 'Invalid file type'}), 400

# @app.route('/update_property_image', methods=['POST'])
def update_property_image(image_path, id):
    try:
        mycursor.execute("""
            UPDATE property_images
            SET image_path = %s
            WHERE image_id = %s
        """, (image_path, id))
        
        mydb.commit()
        print(f'Image for property ID {id} updated to {image_path}')
        return {'success': True, 'message': 'Image updated successfully'}
    
    except Exception as e:
        print(e)
        return {'success': False, 'error': str(e)}



# for i, img in enumerate(os.listdir(image_path), start=1):
#     update_property_image(img, i+16)

def add_videos(image_path, id):
    try:
        # SQL query to update the picture of property with the given property_id
        mycursor.execute("""
            UPDATE videos
            SET file_path = %s
            WHERE id = %s
        """, (image_path, id))
        
        # Commit the transaction to save the changes
        mydb.commit()

        print('Image updated successfully')
        return ({'success': True, 'message': 'Image updated successfully'})
    
    except Exception as e:
        # If an error occurs, handle it and return the error message
        return ({'success': False, 'error': str(e)})



# for i, img in enumerate(os.listdir(videos_path), start=1):
    
#    add_videos(img, i+50)




@app.route('/', methods=['GET'])
def get_items():
    return render_template('index.html'), 200

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')
@app.route('/trending_videos', methods=['GET'])
def lt():
    return render_template('videos.html')

@app.route('/about', methods=['GET'])
def abt():
    return render_template('about.html')

@app.route('/for_sale', methods=['GET'])
def buy():
    return render_template('for_Sale.html')

@app.route('/sell', methods=['GET'])
def sell():
    return render_template('sell.html')

@app.route('/guide', methods=['GET'])
def guide():
    return render_template('guides.html')
   
@app.route('/for_rent', methods=['GET'])
def rent():
    return render_template('rent.html')
   

@app.route('/contact_us', methods=['GET'])
def contact_us():
    return render_template('contactUs.html')
   
@app.route('/more', methods=['GET'])
def more():
    return render_template('more.html')

@app.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)
