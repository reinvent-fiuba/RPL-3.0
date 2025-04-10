CREATE DATABASE IF NOT EXISTS `test_rpl_users`;
CREATE DATABASE IF NOT EXISTS `test_rpl_activities`;

GRANT ALL PRIVILEGES ON `test_rpl_users`.* TO 'test_user'@'%';
GRANT ALL PRIVILEGES ON `test_rpl_activities`.* TO 'test_user'@'%';

