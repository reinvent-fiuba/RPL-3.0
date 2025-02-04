


-- CREATE TABLE alembic_version (
--     version_num VARCHAR(32) NOT NULL, 
--     CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
-- );



CREATE TABLE activity_categories (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    course_id BIGINT, 
    name VARCHAR(255), 
    description VARCHAR(255), 
    active BOOL, 
    date_created DATETIME, 
    last_updated DATETIME, 
    PRIMARY KEY (id)
);

CREATE TABLE rpl_files (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    file_name VARCHAR(255), 
    file_type VARCHAR(255), 
    data BLOB, 
    date_created DATETIME, 
    last_updated DATETIME, 
    PRIMARY KEY (id)
);

CREATE TABLE activities (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    course_id BIGINT, 
    activity_category_id BIGINT, 
    name VARCHAR(500), 
    description TEXT, 
    language VARCHAR(255), 
    is_io_tested BOOL, 
    active BOOL, 
    deleted BOOL, 
    starting_files_id BIGINT, 
    points INTEGER, 
    compilation_flags VARCHAR(500) NOT NULL, 
    date_created DATETIME, 
    last_updated DATETIME, 
    PRIMARY KEY (id), 
    FOREIGN KEY(activity_category_id) REFERENCES activity_categories (id), 
    FOREIGN KEY(starting_files_id) REFERENCES rpl_files (id)
);

CREATE TABLE activity_submissions (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    activity_id BIGINT, 
    user_id BIGINT, 
    response_files_id BIGINT, 
    status VARCHAR(255), 
    is_final_solution BOOL NOT NULL, 
    date_created DATETIME, 
    last_updated DATETIME, 
    PRIMARY KEY (id), 
    FOREIGN KEY(activity_id) REFERENCES activities (id), 
    FOREIGN KEY(response_files_id) REFERENCES rpl_files (id)
);

CREATE TABLE io_tests (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    activity_id BIGINT, 
    name VARCHAR(500), 
    test_in TEXT, 
    test_out TEXT, 
    date_created DATETIME, 
    last_updated DATETIME, 
    PRIMARY KEY (id), 
    FOREIGN KEY(activity_id) REFERENCES activities (id)
);

CREATE TABLE unit_tests (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    activity_id BIGINT, 
    test_file_id BIGINT, 
    date_created DATETIME, 
    last_updated DATETIME, 
    PRIMARY KEY (id), 
    FOREIGN KEY(activity_id) REFERENCES activities (id), 
    FOREIGN KEY(test_file_id) REFERENCES rpl_files (id)
);

CREATE TABLE results (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    activity_submission_id BIGINT, 
    score VARCHAR(255), 
    date_created DATETIME, 
    last_updated DATETIME, 
    PRIMARY KEY (id), 
    FOREIGN KEY(activity_submission_id) REFERENCES activity_submissions (id)
);

CREATE TABLE test_run (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    activity_submission_id BIGINT, 
    success BOOL, 
    exit_message VARCHAR(255), 
    stderr TEXT, 
    stdout TEXT, 
    date_created DATETIME, 
    last_updated DATETIME, 
    PRIMARY KEY (id), 
    FOREIGN KEY(activity_submission_id) REFERENCES activity_submissions (id)
);

CREATE TABLE io_test_run (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    test_run_id BIGINT, 
    test_name VARCHAR(500), 
    test_in TEXT, 
    expected_output TEXT, 
    run_output TEXT, 
    date_created DATETIME, 
    PRIMARY KEY (id), 
    FOREIGN KEY(test_run_id) REFERENCES test_run (id)
);

CREATE TABLE unit_test_run (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    test_run_id BIGINT, 
    name VARCHAR(255), 
    passed BOOL, 
    error_messages TEXT, 
    date_created DATETIME, 
    PRIMARY KEY (id), 
    FOREIGN KEY(test_run_id) REFERENCES test_run (id)
);

-- INSERT INTO alembic_version (version_num) VALUES ('8acb53cbf546');