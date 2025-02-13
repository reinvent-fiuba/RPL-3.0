USE rpl_users;
RENAME TABLE validation_token TO validation_tokens;

USE rpl_activities;
RENAME TABLE unit_test_run TO unit_test_runs, io_test_run TO io_test_runs, test_run TO test_runs;
