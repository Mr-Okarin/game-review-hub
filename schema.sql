        -- SQL commands to create the database tables
        -- Make sure the database itself (e.g., game_review_db) exists before running these,
        -- or modify the init_db.py script to create it.

        CREATE TABLE IF NOT EXISTS Users (
            user_id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            bio TEXT NULL,
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin BOOLEAN DEFAULT FALSE,
            profile_picture_url VARCHAR(255) NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

        CREATE TABLE IF NOT EXISTS Genres (
            genre_id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(50) UNIQUE NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

        CREATE TABLE IF NOT EXISTS Games (
            game_id INT PRIMARY KEY AUTO_INCREMENT,
            title VARCHAR(150) NOT NULL,
            description TEXT NULL,
            release_date DATE NULL,
            developer VARCHAR(100) NULL,
            platform VARCHAR(100) NULL,
            cover_image_url VARCHAR(255) NULL,
            trailer_url VARCHAR(255) NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

        CREATE TABLE IF NOT EXISTS Game_Genres (
            game_id INT NOT NULL,
            genre_id INT NOT NULL,
            PRIMARY KEY (game_id, genre_id),
            FOREIGN KEY (game_id) REFERENCES Games(game_id) ON DELETE CASCADE,
            FOREIGN KEY (genre_id) REFERENCES Genres(genre_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

        CREATE TABLE IF NOT EXISTS Reviews (
            review_id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            game_id INT NOT NULL,
            rating INT, -- CHECK constraint handled differently or omitted in basic setup script
            comment TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_approved BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (game_id) REFERENCES Games(game_id) ON DELETE CASCADE
            -- Adding explicit CHECK constraint for MySQL 8.0.16+ if needed, but often omitted in simple init scripts
            -- CONSTRAINT chk_rating CHECK (rating >= 1 AND rating <= 5)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

        CREATE TABLE IF NOT EXISTS Likes (
            like_id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            review_id INT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_user_review_like (user_id, review_id),
            FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (review_id) REFERENCES Reviews(review_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

        CREATE TABLE IF NOT EXISTS Notifications (
            notification_id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            notification_type VARCHAR(50) NOT NULL,
            text VARCHAR(255) NOT NULL,
            link VARCHAR(255) NULL,
            is_read BOOLEAN DEFAULT FALSE,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

        CREATE TABLE IF NOT EXISTS Reports (
            report_id INT PRIMARY KEY AUTO_INCREMENT,
            reporter_user_id INT NOT NULL,
            reported_user_id INT NULL,
            reported_review_id INT NULL,
            reason TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'pending', -- CHECK constraint handled differently or omitted
            admin_notes TEXT NULL,
            FOREIGN KEY (reporter_user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (reported_user_id) REFERENCES Users(user_id) ON DELETE SET NULL,
            FOREIGN KEY (reported_review_id) REFERENCES Reviews(review_id) ON DELETE SET NULL
            -- Adding explicit CHECK constraint for MySQL 8.0.16+ if needed
            -- CONSTRAINT chk_status CHECK (status IN ('pending', 'resolved', 'dismissed')),
            -- CONSTRAINT chk_report_target CHECK (reported_user_id IS NOT NULL OR reported_review_id IS NOT NULL)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

        CREATE TABLE IF NOT EXISTS Preferences (
            preference_id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            preference_type VARCHAR(50) NOT NULL,
            preference_value VARCHAR(100) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

        CREATE TABLE IF NOT EXISTS Wishlist_Items (
            user_id INT NOT NULL,
            game_id INT NOT NULL,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, game_id),
            FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (game_id) REFERENCES Games(game_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        