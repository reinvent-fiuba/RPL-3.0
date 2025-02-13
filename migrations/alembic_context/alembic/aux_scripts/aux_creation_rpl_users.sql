
-- CREATE TABLE alembic_version (
--     version_num VARCHAR(32) NOT NULL, 
    -- CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
-- );



CREATE TABLE courses (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    name VARCHAR(255), 
    university VARCHAR(255), 
    university_course_id VARCHAR(255), 
    description VARCHAR(255), 
    active BOOL, 
    deleted BOOL, 
    semester VARCHAR(255), 
    semester_start_date DATETIME, 
    `semester_END_date` DATETIME, 
    img_uri VARCHAR(255), 
    date_created DATETIME, 
    last_updated DATETIME, 
    PRIMARY KEY (id)
);

CREATE TABLE permissions (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    name VARCHAR(50), 
    date_created DATETIME, 
    PRIMARY KEY (id)
);

CREATE TABLE roles (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    name VARCHAR(50), 
    permissions VARCHAR(1000), 
    date_created DATETIME, 
    last_updated DATETIME, 
    PRIMARY KEY (id)
);

CREATE TABLE users (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    name VARCHAR(255), 
    surname VARCHAR(255), 
    student_id VARCHAR(255), 
    username VARCHAR(255) NOT NULL, 
    email VARCHAR(255) NOT NULL, 
    password VARCHAR(255) NOT NULL, 
    email_validated BOOL NOT NULL, 
    is_admin BOOL, 
    degree VARCHAR(255), 
    university VARCHAR(255), 
    date_created DATETIME, 
    last_updated DATETIME, 
    img_uri VARCHAR(255), 
    PRIMARY KEY (id), 
    UNIQUE (email), 
    UNIQUE (username)
);

CREATE TABLE course_users (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    course_id BIGINT, 
    user_id BIGINT, 
    role_id BIGINT, 
    accepted BOOL, 
    date_created DATETIME, 
    last_updated DATETIME, 
    PRIMARY KEY (id), 
    FOREIGN KEY(course_id) REFERENCES courses (id), 
    FOREIGN KEY(role_id) REFERENCES roles (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE validation_token (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    user_id BIGINT, 
    token VARCHAR(255), 
    expiry_date DATETIME, 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

-- INSERT INTO alembic_version (version_num) VALUES ('7a171565597e');