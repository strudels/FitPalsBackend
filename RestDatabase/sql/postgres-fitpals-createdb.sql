CREATE EXTENSION IF NOT EXISTS postgis;
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    fb_id VARCHAR(2048) UNIQUE NOT NULL,
    location GEOMETRY,
    about_me TEXT,
    primary_picture VARCHAR(2048),
    last_updated TIMESTAMP,
    dob BIGINT,
    available BOOLEAN,
    jabber_id VARCHAR(2048) UNIQUE NOT NULL,
);

DROP INDEX IF EXISTS geolocation_index;
CREATE INDEX geolocation_index ON users USING GIST (location);

CREATE OR REPLACE FUNCTION update_users_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER `users_last_updated` AFTER INSERT OR UPDATE on `users`
    FOR EACH ROW EXECUTE PROCEDURE update_users_last_updated()

CREATE TABLE IF NOT EXISTS secondary_pictures (
    user_id INTEGER NOT NULL,
    link VARCHAR(2048) NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS approved_users (
    user_id INTEGER NOT NULL,
    approved_user INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS denied_users (
    user_id INTEGER NOT NULL,
    denied_user INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS apn_tokens (
    user_id INTEGER NOT NULL,
    token VARCHAR(64),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TYPE activity_name AS ENUM('running','walking','jogging','strolling');
CREATE TABLE IF NOT EXISTS activities (
    activity_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name activity_name UNIQUE NOT NULL,
    miles DOUBLE PRECISION, 
    seconds INTEGER
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);
