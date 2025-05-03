# --- app.py ---
# Flask application with MySQL support, Auth, Reviews, Wishlist, Admin, Search, Suggestions, Profile/Preferences
# Added: Genres for Game Detail Page

import mysql.connector
from flask import (Flask, render_template, g, abort, request,
                   redirect, url_for, session, flash, current_app)
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps

# --- Configuration ---
DB_CONFIG_MYSQL = {
    'user': 'root',
    'password': '', # UPDATE IF YOU SET A PASSWORD
    'host': '127.0.0.1',
    'database': 'game_review_db', # VERIFY DATABASE NAME
    'raise_on_warnings': True,
    'autocommit': False
}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a-default-fallback-secret-key-for-dev-genres')

# --- Database Helper Functions ---
def get_db():
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(**DB_CONFIG_MYSQL)
        except mysql.connector.Error as err:
            print(f"MySQL connection error: {err}")
            abort(500, description=f"Database connection failed: {err}")
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        try: db.close()
        except Exception as e: print(f"Error closing database connection: {e}")

def get_cursor():
    db = get_db()
    try:
        return db.cursor(dictionary=True)
    except (mysql.connector.Error, AttributeError) as e:
         print(f"Error getting cursor: {e}")
         abort(500, description="Could not create database cursor.")

# --- User Loader & Decorators ---
@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    g.user = None
    if user_id is not None:
        try:
            cursor = get_cursor()
            cursor.execute("SELECT user_id, username, is_admin FROM Users WHERE user_id = %s", (user_id,))
            g.user = cursor.fetchone()
            cursor.close()
        except mysql.connector.Error as e:
             print(f"Error fetching user {user_id} from DB: {e}")

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('You need to be logged in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or not g.user.get('is_admin'):
            flash('You must be an administrator to access this page.', 'error')
            return redirect(url_for('index'))
        return view(**kwargs)
    return wrapped_view

# --- Authentication Routes ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if g.user: return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        error = None
        if not username: error = 'Username is required.'
        elif not email: error = 'Email is required.'
        elif not password: error = 'Password is required.'
        elif password != confirm_password: error = 'Passwords do not match.'
        if error is None:
            try:
                db = get_db()
                cursor = get_cursor()
                cursor.execute("SELECT user_id FROM Users WHERE username = %s", (username,))
                if cursor.fetchone() is not None: error = f"Username '{username}' is already taken."
                else:
                    cursor.execute("SELECT user_id FROM Users WHERE email = %s", (email,))
                    if cursor.fetchone() is not None: error = f"Email '{email}' is already registered."
                if error is None:
                    hashed_password = generate_password_hash(password)
                    insert_query = "INSERT INTO Users (username, email, password_hash) VALUES (%s, %s, %s)"
                    cursor.execute(insert_query, (username, email, hashed_password))
                    db.commit()
                    cursor.close()
                    flash('Account created successfully! Please log in.', 'success')
                    return redirect(url_for('login'))
                cursor.close()
            except mysql.connector.Error as e:
                db.rollback()
                print(f"Database error during signup: {e}")
                error = "An error occurred during registration. Please try again."
        if error: flash(error, 'error')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user: return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None
        user = None
        if not username: error = 'Username is required.'
        elif not password: error = 'Password is required.'
        if error is None:
            try:
                cursor = get_cursor()
                cursor.execute("SELECT user_id, username, password_hash, is_admin FROM Users WHERE username = %s", (username,))
                user = cursor.fetchone()
                cursor.close()
                if user is None: error = 'Incorrect username.'
                elif not check_password_hash(user['password_hash'], password): error = 'Incorrect password.'
            except mysql.connector.Error as e:
                 print(f"Database error during login: {e}")
                 error = "An error occurred during login. Please try again."
        if error is None and user is not None:
            session.clear()
            session['user_id'] = user['user_id']
            flash(f'Welcome back, {user["username"]}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
             flash(error, 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# --- Main Application Routes ---
@app.route('/')
def index():
    """ Renders the home page and fetches suggestions for logged-in users. """
    suggestions = []
    if g.user:
        user_id = g.user['user_id']
        try:
            cursor = get_cursor()
            pref_query = "SELECT preference_value FROM Preferences WHERE user_id = %s AND preference_type = 'genre'"
            cursor.execute(pref_query, (user_id,))
            preferred_genres_result = cursor.fetchall()
            preferred_genres = [row['preference_value'] for row in preferred_genres_result]

            if preferred_genres:
                wishlist_query = "SELECT game_id FROM Wishlist_Items WHERE user_id = %s"
                cursor.execute(wishlist_query, (user_id,))
                wishlist_ids_result = cursor.fetchall()
                wishlist_ids = {row['game_id'] for row in wishlist_ids_result}

                reviewed_query = "SELECT DISTINCT game_id FROM Reviews WHERE user_id = %s"
                cursor.execute(reviewed_query, (user_id,))
                reviewed_ids_result = cursor.fetchall()
                reviewed_ids = {row['game_id'] for row in reviewed_ids_result}

                excluded_ids = wishlist_ids.union(reviewed_ids)
                excluded_ids_list = list(excluded_ids)

                genre_placeholders = ', '.join(['%s'] * len(preferred_genres))
                if excluded_ids_list:
                    excluded_placeholders = ', '.join(['%s'] * len(excluded_ids_list))
                    not_in_clause = f"AND g.game_id NOT IN ({excluded_placeholders})"
                    params = preferred_genres + excluded_ids_list
                else:
                    not_in_clause = ""
                    params = preferred_genres

                suggestion_query = f"""
                    SELECT DISTINCT g.game_id, g.title, g.cover_image_url
                    FROM Games g
                    JOIN Game_Genres gg ON g.game_id = gg.game_id
                    JOIN Genres gen ON gg.genre_id = gen.genre_id
                    WHERE gen.name IN ({genre_placeholders})
                      {not_in_clause}
                    ORDER BY RAND() LIMIT 5
                """
                cursor.execute(suggestion_query, params)
                suggestions = cursor.fetchall()
            cursor.close()
        except mysql.connector.Error as e:
            print(f"Database error fetching suggestions for user {user_id}: {e}")
            suggestions = []
        except Exception as e:
             print(f"Unexpected error fetching suggestions: {e}")
             suggestions = []
    return render_template('index.html', suggestions=suggestions)

@app.route('/games')
def list_games():
    games = []
    try:
        cursor = get_cursor()
        cursor.execute("SELECT game_id, title, developer, platform, cover_image_url FROM Games ORDER BY title COLLATE utf8mb4_general_ci ASC")
        games = cursor.fetchall()
        cursor.close()
    except mysql.connector.Error as e:
        print(f"Database error in /games route: {e}")
        abort(500, description="An error occurred while fetching games.")
    return render_template('games.html', games=games)

# --- MODIFIED game_detail route ---
@app.route('/game/<int:game_id>', methods=['GET', 'POST'])
def game_detail(game_id):
    """ Fetches details, reviews, genres, wishlist status; handles review submission. """
    game = None
    reviews = []
    genres = [] # <-- Initialize list for genres
    is_in_wishlist = False

    # Handle Review Submission
    if request.method == 'POST' and 'comment' in request.form:
        if g.user is None:
            flash('You must be logged in to submit a review.', 'warning')
            return redirect(url_for('login', next=request.url))
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment')
        user_id = g.user['user_id']
        error = None
        if rating is None or not (1 <= rating <= 5): error = 'Invalid rating.'
        elif not comment or not comment.strip(): error = 'Comment cannot be empty.'
        if error is None:
            try:
                db = get_db()
                cursor = get_cursor()
                query = "INSERT INTO Reviews (user_id, game_id, rating, comment) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (user_id, game_id, rating, comment))
                db.commit()
                cursor.close()
                flash('Review submitted successfully!', 'success')
                return redirect(url_for('game_detail', game_id=game_id))
            except mysql.connector.Error as e:
                db.rollback()
                print(f"Database error submitting review: {e}")
                flash('An error occurred while submitting your review.', 'error')
        else:
            flash(error, 'error')

    # Fetch Game Details, Reviews, Genres, and Wishlist Status
    try:
        cursor = get_cursor()
        # Fetch game details
        game_query = "SELECT game_id, title, description, developer, platform, release_date, cover_image_url, trailer_url FROM Games WHERE game_id = %s"
        cursor.execute(game_query, (game_id,))
        game = cursor.fetchone()

        if game is None:
            cursor.close()
            abort(404, description="Game not found.")

        # Fetch reviews
        reviews_query = """
            SELECT r.review_id, r.rating, r.comment, r.timestamp, u.username
            FROM Reviews r JOIN Users u ON r.user_id = u.user_id
            WHERE r.game_id = %s AND r.is_approved = TRUE
            ORDER BY r.timestamp DESC
        """
        cursor.execute(reviews_query, (game_id,))
        reviews = cursor.fetchall()

        # *** NEW: Fetch genres for this game ***
        genres_query = """
            SELECT gen.name
            FROM Genres gen
            JOIN Game_Genres gg ON gen.genre_id = gg.genre_id
            WHERE gg.game_id = %s
            ORDER BY gen.name ASC
        """
        cursor.execute(genres_query, (game_id,))
        genres = cursor.fetchall() # Will be list of dicts like [{'name': 'RPG'}, {'name': 'Action'}]

        # Check wishlist status
        if g.user:
            wishlist_query = "SELECT 1 FROM Wishlist_Items WHERE user_id = %s AND game_id = %s"
            cursor.execute(wishlist_query, (g.user['user_id'], game_id))
            if cursor.fetchone():
                is_in_wishlist = True

        cursor.close() # Close cursor after all fetches

    except mysql.connector.Error as e:
        print(f"Database error fetching game details/reviews/genres/wishlist for game {game_id}: {e}")
        abort(500, description="An error occurred while fetching game data.")

    # Render template, passing genres along with other data
    return render_template('game_detail.html',
                           game=game,
                           reviews=reviews,
                           genres=genres, # <-- Pass genres to template
                           is_in_wishlist=is_in_wishlist)


# --- Wishlist Routes ---
@app.route('/wishlist')
@login_required
def view_wishlist():
    wishlist_games = []
    user_id = g.user['user_id']
    try:
        cursor = get_cursor()
        query = "SELECT g.game_id, g.title, g.cover_image_url, g.developer FROM Wishlist_Items w JOIN Games g ON w.game_id = g.game_id WHERE w.user_id = %s ORDER BY g.title COLLATE utf8mb4_general_ci ASC"
        cursor.execute(query, (user_id,))
        wishlist_games = cursor.fetchall()
        cursor.close()
    except mysql.connector.Error as e:
        print(f"Database error fetching wishlist for user {user_id}: {e}")
        flash('Could not load your wishlist.', 'error')
        return redirect(url_for('index'))
    return render_template('wishlist.html', wishlist_games=wishlist_games)

@app.route('/wishlist/add/<int:game_id>', methods=['POST'])
@login_required
def add_to_wishlist(game_id):
    user_id = g.user['user_id']
    try:
        db = get_db()
        cursor = get_cursor()
        query = "INSERT IGNORE INTO Wishlist_Items (user_id, game_id) VALUES (%s, %s)"
        cursor.execute(query, (user_id, game_id))
        db.commit()
        cursor.close()
        flash('Game added to your wishlist!', 'success')
    except mysql.connector.Error as e:
        db.rollback()
        print(f"Database error adding game {game_id} to wishlist for user {user_id}: {e}")
        flash('Could not add game to wishlist.', 'error')
    return redirect(url_for('game_detail', game_id=game_id))

@app.route('/wishlist/remove/<int:game_id>', methods=['POST'])
@login_required
def remove_from_wishlist(game_id):
    user_id = g.user['user_id']
    try:
        db = get_db()
        cursor = get_cursor()
        query = "DELETE FROM Wishlist_Items WHERE user_id = %s AND game_id = %s"
        cursor.execute(query, (user_id, game_id))
        db.commit()
        cursor.close()
        flash('Game removed from your wishlist.', 'info')
    except mysql.connector.Error as e:
        db.rollback()
        print(f"Database error removing game {game_id} from wishlist for user {user_id}: {e}")
        flash('Could not remove game from wishlist.', 'error')
    return redirect(request.referrer or url_for('game_detail', game_id=game_id))

# --- Profile Route ---
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = g.user['user_id']
    all_genres = []
    current_prefs = set()
    try:
        cursor = get_cursor()
        cursor.execute("SELECT genre_id, name FROM Genres ORDER BY name ASC")
        all_genres = cursor.fetchall()
        cursor.execute("SELECT preference_value FROM Preferences WHERE user_id = %s AND preference_type = 'genre'", (user_id,))
        current_prefs_result = cursor.fetchall()
        current_prefs = {row['preference_value'] for row in current_prefs_result}
        cursor.close()
    except mysql.connector.Error as e:
        print(f"Database error fetching profile data for user {user_id}: {e}")
        flash('Could not load profile data.', 'error')
        return redirect(url_for('index'))
    if request.method == 'POST':
        selected_genre_names = request.form.getlist('preferred_genres')
        db = get_db()
        cursor = None
        try:
            cursor = get_cursor()
            cursor.execute("DELETE FROM Preferences WHERE user_id = %s AND preference_type = 'genre'", (user_id,))
            if selected_genre_names:
                insert_data = [(user_id, 'genre', genre_name) for genre_name in selected_genre_names]
                query = "INSERT INTO Preferences (user_id, preference_type, preference_value) VALUES (%s, %s, %s)"
                cursor.executemany(query, insert_data)
            db.commit()
            cursor.close()
            flash('Your preferences have been updated!', 'success')
            current_prefs = set(selected_genre_names)
        except mysql.connector.Error as e:
            db.rollback()
            print(f"Database error updating preferences for user {user_id}: {e}")
            flash('An error occurred while updating your preferences.', 'error')
        finally:
            if cursor: cursor.close()
    return render_template('profile.html',
                           all_genres=all_genres,
                           current_preferences=current_prefs)

# --- Admin Routes ---
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/add_game', methods=['GET', 'POST'])
@login_required
@admin_required
def add_game():
    genres = []
    try:
        cursor = get_cursor()
        cursor.execute("SELECT genre_id, name FROM Genres ORDER BY name ASC")
        genres = cursor.fetchall()
        cursor.close()
    except mysql.connector.Error as e:
        print(f"Database error fetching genres for add_game form: {e}")
        flash('Could not load genres for the form.', 'error')
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        release_date_str = request.form.get('release_date')
        release_date = release_date_str if release_date_str else None
        developer = request.form.get('developer')
        platform = request.form.get('platform')
        cover_image_url = request.form.get('cover_image_url')
        trailer_url = request.form.get('trailer_url')
        selected_genre_ids = request.form.getlist('genre_ids', type=int)
        error = None
        if not title: error = 'Game title is required.'
        if error is None:
            db = get_db()
            cursor = None
            try:
                cursor = get_cursor()
                game_query = "INSERT INTO Games (title, description, release_date, developer, platform, cover_image_url, trailer_url) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(game_query, (title, description, release_date, developer, platform, cover_image_url, trailer_url))
                new_game_id = cursor.lastrowid
                if new_game_id and selected_genre_ids:
                    genre_data = [(new_game_id, genre_id) for genre_id in selected_genre_ids]
                    genre_query = "INSERT INTO Game_Genres (game_id, genre_id) VALUES (%s, %s)"
                    cursor.executemany(genre_query, genre_data)
                db.commit()
                flash(f"Game '{title}' added successfully!", 'success')
                if cursor: cursor.close()
                return redirect(url_for('game_detail', game_id=new_game_id))
            except mysql.connector.Error as e:
                db.rollback()
                print(f"Database error adding game: {e}")
                flash('An error occurred while adding the game.', 'error')
            finally:
                if cursor: cursor.close()
        else:
            flash(error, 'error')
    return render_template('admin/add_game.html', genres=genres)

@app.route('/admin/manage_games')
@login_required
@admin_required
def manage_games():
    games = []
    try:
        cursor = get_cursor()
        cursor.execute("SELECT game_id, title, developer FROM Games ORDER BY title ASC")
        games = cursor.fetchall()
        cursor.close()
    except mysql.connector.Error as e:
        print(f"Database error fetching games for management: {e}")
        flash('Could not load games list.', 'error')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/manage_games.html', games=games)

@app.route('/admin/edit_game/<int:game_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_game(game_id):
    game = None
    all_genres = []
    current_genre_ids = set()
    try:
        cursor = get_cursor()
        cursor.execute("SELECT * FROM Games WHERE game_id = %s", (game_id,))
        game = cursor.fetchone()
        if not game:
            flash('Game not found.', 'error')
            cursor.close()
            return redirect(url_for('manage_games'))
        cursor.execute("SELECT genre_id, name FROM Genres ORDER BY name ASC")
        all_genres = cursor.fetchall()
        cursor.execute("SELECT genre_id FROM Game_Genres WHERE game_id = %s", (game_id,))
        current_genres_result = cursor.fetchall()
        current_genre_ids = {row['genre_id'] for row in current_genres_result}
        cursor.close()
    except mysql.connector.Error as e:
        print(f"Database error fetching data for edit_game {game_id}: {e}")
        flash('Could not load game data for editing.', 'error')
        return redirect(url_for('manage_games'))
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        release_date_str = request.form.get('release_date')
        release_date = release_date_str if release_date_str else None
        developer = request.form.get('developer')
        platform = request.form.get('platform')
        cover_image_url = request.form.get('cover_image_url')
        trailer_url = request.form.get('trailer_url')
        selected_genre_ids = request.form.getlist('genre_ids', type=int)
        error = None
        if not title: error = 'Game title is required.'
        if error is None:
            db = get_db()
            cursor = None
            try:
                cursor = get_cursor()
                game_update_query = "UPDATE Games SET title = %s, description = %s, release_date = %s, developer = %s, platform = %s, cover_image_url = %s, trailer_url = %s WHERE game_id = %s"
                cursor.execute(game_update_query, (title, description, release_date, developer, platform, cover_image_url, trailer_url, game_id))
                cursor.execute("DELETE FROM Game_Genres WHERE game_id = %s", (game_id,))
                if selected_genre_ids:
                    genre_data = [(game_id, genre_id) for genre_id in selected_genre_ids]
                    genre_insert_query = "INSERT INTO Game_Genres (game_id, genre_id) VALUES (%s, %s)"
                    cursor.executemany(genre_insert_query, genre_data)
                db.commit()
                flash(f"Game '{title}' updated successfully!", 'success')
                if cursor: cursor.close()
                return redirect(url_for('manage_games'))
            except mysql.connector.Error as e:
                db.rollback()
                print(f"Database error updating game {game_id}: {e}")
                flash('An error occurred while updating the game.', 'error')
            finally:
                if cursor: cursor.close()
        else:
            flash(error, 'error')
    return render_template('admin/edit_game.html', game=game, all_genres=all_genres, current_genre_ids=current_genre_ids)

@app.route('/admin/delete_review/<int:review_id>', methods=['POST'])
@login_required
@admin_required
def delete_review(review_id):
    game_id = None
    db = get_db()
    cursor = None
    try:
        cursor = get_cursor()
        cursor.execute("SELECT game_id FROM Reviews WHERE review_id = %s", (review_id,))
        result = cursor.fetchone()
        if result: game_id = result['game_id']
        cursor.execute("DELETE FROM Reviews WHERE review_id = %s", (review_id,))
        db.commit()
        flash('Review deleted successfully.', 'success')
    except mysql.connector.Error as e:
        db.rollback()
        print(f"Database error deleting review {review_id}: {e}")
        flash('An error occurred while deleting the review.', 'error')
    finally:
        if cursor: cursor.close()
    if game_id: return redirect(url_for('game_detail', game_id=game_id))
    else: return redirect(url_for('admin_dashboard'))

# --- Search Route ---
@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    search_results = []
    error = None
    if not query:
        error = "Please enter a search term."
    else:
        try:
            cursor = get_cursor()
            sql_query = "SELECT game_id, title, developer, platform, cover_image_url FROM Games WHERE title LIKE %s ORDER BY title COLLATE utf8mb4_general_ci ASC"
            search_term = f"%{query}%"
            cursor.execute(sql_query, (search_term,))
            search_results = cursor.fetchall()
            cursor.close()
        except mysql.connector.Error as e:
            print(f"Database error during search for '{query}': {e}")
            error = "An error occurred during the search."
    if error: flash(error, 'error')
    return render_template('search_results.html', query=query, results=search_results)

# --- Error Handling ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e), 404

@app.errorhandler(500)
def internal_server_error(e):
    if hasattr(g, 'db') and g.db is not None:
         try: g.db.rollback()
         except mysql.connector.Error as rollback_err: print(f"Error during rollback: {rollback_err}")
    return render_template('500.html', error=e), 500

# --- Running the App ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

