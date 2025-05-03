        -- SQL commands to insert sample data
        -- Run this AFTER schema.sql has been executed successfully.

        -- Clear existing data to avoid duplicate errors if run multiple times
        -- Use with caution! This deletes all data in these tables.
        DELETE FROM Wishlist_Items;
        DELETE FROM Preferences;
        DELETE FROM Reports;
        DELETE FROM Notifications;
        DELETE FROM Likes;
        DELETE FROM Reviews;
        DELETE FROM Game_Genres;
        DELETE FROM Games;
        DELETE FROM Genres;
        DELETE FROM Users;

        -- Reset auto_increment counters (optional, but good for consistency)
        ALTER TABLE Users AUTO_INCREMENT = 1;
        ALTER TABLE Genres AUTO_INCREMENT = 1;
        ALTER TABLE Games AUTO_INCREMENT = 1;
        ALTER TABLE Reviews AUTO_INCREMENT = 1;
        ALTER TABLE Likes AUTO_INCREMENT = 1;
        ALTER TABLE Notifications AUTO_INCREMENT = 1;
        ALTER TABLE Reports AUTO_INCREMENT = 1;
        ALTER TABLE Preferences AUTO_INCREMENT = 1;
        -- No auto_increment for Wishlist_Items or Game_Genres

        -- Insert Sample Data
        -- NOTE: Sample passwords here are just placeholders. Sign up new users via the web interface.
        INSERT INTO Users (username, email, password_hash, bio, is_admin) VALUES
        ('GamerGal', 'gal@email.com', '$pbkdf2-sha256$29000$examplehash1.salt$hashedpassword1', 'Loves RPGs and indie games.', FALSE),
        ('ActionFan', 'action@email.com', '$pbkdf2-sha256$29000$examplehash2.salt$hashedpassword2', 'Plays all the latest AAA action titles.', FALSE),
        ('AdminUser', 'admin@email.com', '$pbkdf2-sha256$29000$examplehashA.salt$hashedpasswordA', 'Site administrator.', TRUE); -- Remember to set is_admin=1 via phpMyAdmin or signup/edit later

        INSERT INTO Genres (name) VALUES
        ('RPG'), ('Action'), ('Strategy'), ('Indie'), ('Puzzle'),
        ('Simulation'), ('Adventure'), ('Shooter'), ('Platformer'), ('Fighting');

        INSERT INTO Games (title, description, release_date, developer, platform, cover_image_url, trailer_url) VALUES
        ('Elden Ring', 'Vast open-world action RPG with challenging combat.', '2022-02-25', 'FromSoftware', 'PC, PS5, PS4, Xbox Series X/S, Xbox One', 'https://placehold.co/300x400/2a2a2a/ffffff?text=Elden+Ring', 'https://example.com/trailer_er'),
        ('Cyberpunk 2077', 'Action RPG set in the futuristic Night City.', '2020-12-10', 'CD Projekt Red', 'PC, PS5, PS4, Xbox Series X/S, Xbox One, Stadia', 'https://placehold.co/300x400/3a3a3a/ffffff?text=Cyberpunk+2077', 'https://example.com/trailer_cp'),
        ('Stardew Valley', 'Relaxing farming simulation RPG.', '2016-02-26', 'ConcernedApe', 'PC, Mac, Linux, PS4, Xbox One, Switch, iOS, Android', 'https://placehold.co/300x400/4a4a4a/ffffff?text=Stardew+Valley', 'https://example.com/trailer_sv'),
        ('Hades', 'Roguelike dungeon crawler with Greek mythology theme.', '2020-09-17', 'Supergiant Games', 'PC, Mac, Switch, PS4, PS5, Xbox One, Xbox Series X/S', 'https://placehold.co/300x400/5a5a5a/ffffff?text=Hades', 'https://example.com/trailer_hades'),
        ('Civilization VI', 'Turn-based strategy game where you build an empire.', '2016-10-21', 'Firaxis Games', 'PC, Mac, Linux, PS4, Xbox One, Switch, iOS, Android', 'https://placehold.co/300x400/6a6a6a/ffffff?text=Civilization+VI', 'https://example.com/trailer_civ6'),
        ('Portal 2', 'First-person puzzle-platformer with portals.', '2011-04-19', 'Valve', 'PC, Mac, Linux, PS3, Xbox 360', 'https://placehold.co/300x400/7a7a7a/ffffff?text=Portal+2', 'https://example.com/trailer_p2'),
        ('The Legend of Zelda: Tears of the Kingdom', 'Open-world action-adventure game.', '2023-05-12', 'Nintendo EPD', 'Switch', 'https://placehold.co/300x400/8a8a8a/ffffff?text=Zelda:+TotK', 'https://example.com/trailer_totk'),
        ('Counter-Strike 2', 'Tactical first-person shooter.', '2023-09-27', 'Valve', 'PC', 'https://placehold.co/300x400/9a9a9a/ffffff?text=CS2', 'https://example.com/trailer_cs2'),
        ('Street Fighter 6', 'Latest installment in the classic fighting game series.', '2023-06-02', 'Capcom', 'PC, PS5, PS4, Xbox Series X/S', 'https://placehold.co/300x400/aaaaaa/ffffff?text=Street+Fighter+6', 'https://example.com/trailer_sf6');

        INSERT INTO Game_Genres (game_id, genre_id) VALUES
        (1, 1), (1, 2),
        (2, 1), (2, 2), (2, 8),
        (3, 6), (3, 1), (3, 4),
        (4, 2), (4, 4), (4, 7),
        (5, 3),
        (6, 5), (6, 9), (6, 7),
        (7, 7), (7, 2), (7, 1),
        (8, 8), (8, 2),
        (9, 10), (9, 2);

        INSERT INTO Reviews (user_id, game_id, rating, comment, is_approved) VALUES
        (1, 1, 5, 'Incredible open world, challenging but rewarding!', TRUE),
        (2, 1, 4, 'Great game, but very difficult sometimes.', TRUE),
        (2, 2, 4, 'Night City is amazing, some bugs though.', TRUE),
        (1, 3, 5, 'So relaxing and addictive. Perfect farm sim.', TRUE),
        (1, 4, 5, 'Masterpiece of storytelling and gameplay.', TRUE),
        (2, 5, 5, 'Just one more turn... forever!', TRUE);

        INSERT INTO Likes (user_id, review_id) VALUES
        (2, 1),
        (1, 3),
        (1, 6);

        INSERT INTO Wishlist_Items (user_id, game_id) VALUES
        (1, 2),
        (1, 5),
        (2, 3),
        (2, 7);

        INSERT INTO Preferences (user_id, preference_type, preference_value) VALUES
        (1, 'genre', 'RPG'),
        (1, 'genre', 'Indie'),
        (2, 'genre', 'Action'),
        (2, 'platform', 'PC');

        INSERT INTO Notifications (user_id, notification_type, text, link, is_read) VALUES
        (1, 'new_review', 'ActionFan reviewed Elden Ring.', '/game/1', FALSE);

        INSERT INTO Reports (reporter_user_id, reported_review_id, reason, status) VALUES
        (2, 4, 'This review contains spoilers without warning.', 'pending');

        