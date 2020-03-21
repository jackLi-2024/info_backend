CREATE DEFINER=`root`@`%` FUNCTION `queryChildren`( Id INT ) RETURNS varchar(4000) CHARSET utf8
BEGIN
	DECLARE
		sTemp VARCHAR ( 4000 );
	DECLARE
		sTempChd VARCHAR ( 4000 );

	SET sTemp = '$';

	SET sTempChd = CAST( Id AS CHAR );
	WHILE
			sTempChd IS NOT NULL DO

			SET sTemp = CONCAT( sTemp, ',', sTempChd );
		SELECT
			GROUP_CONCAT( log_id ) INTO sTempChd
		FROM
			log
		WHERE
			FIND_IN_SET( parent_log_id, sTempChd ) > 0;

	END WHILE;
	RETURN sTemp;

END;