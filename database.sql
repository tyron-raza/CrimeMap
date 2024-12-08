CREATE DATABASE crimemap;
USE crimemap;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('public', 'law', 'admin') DEFAULT 'public'
);



CREATE TABLE crimes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    date_time DATETIME NOT NULL,
    location VARCHAR(255) NOT NULL,
    crime_type VARCHAR(100) NOT NULL,
    media_file VARCHAR(255),
    reported_by INT,
    FOREIGN KEY (reported_by) REFERENCES users(id)
);


ALTER TABLE crimes 
ADD latitude FLOAT NOT NULL, 
ADD longitude FLOAT NOT NULL;



CREATE TABLE crime_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255) NOT NULL,
    date_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    crime_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

