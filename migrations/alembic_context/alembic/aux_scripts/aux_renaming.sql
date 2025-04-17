USE rpl_users;
RENAME TABLE validation_token TO validation_tokens;
ALTER TABLE courses RENAME COLUMN university_course_id TO subject_id;
ALTER TABLE courses RENAME COLUMN semester_END_date TO semester_end_date;
UPDATE roles SET name = 'course_admin', last_updated = UTC_TIMESTAMP() WHERE id=1;
ALTER TABLE validation_tokens RENAME COLUMN expiry_date TO expiration_date;
INSERT INTO universities (id, name, degrees) VALUES (1, 'FIUBA', 'Ingeniería en Informática,Licenciatura en Sistemas,Ingeniería Civil,Ingeniería de Alimentos,Ingeniería Electricista,Ingeniería Electrónica,Ingeniería en Agrimensura,Ingeniería en Petróleo,Ingeniería Industrial,Ingeniería Mecánica,Ingeniería Naval y Mecánica,Ingeniería Química');

USE rpl_activities;
RENAME TABLE unit_test_run TO unit_test_runs, io_test_run TO io_test_runs, test_run TO test_runs;
