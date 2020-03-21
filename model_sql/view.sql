DROP VIEW IF EXISTS  info_view;
CREATE VIEW info_view AS SELECT
	info.*,
	users.phone AS user_phone,
	users.nick AS user_nick
FROM
	info,
	users
WHERE
	info.uid = users.uid;


