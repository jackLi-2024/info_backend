CREATE TABLE
IF
	NOT EXISTS `users` (
		`uid` VARCHAR ( 255 ) NOT NULL COMMENT '用户id（基于手机号的加密）',
		`nick` VARCHAR ( 50 ) COMMENT '用户昵称',
		`avatar` VARCHAR ( 50 ) COMMENT '头像(上传baseb4)',
		`create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
		`phone` VARCHAR ( 255 ) NOT NULL COMMENT '用户手机号',
		`password` VARCHAR ( 255 ) NOT NULL COMMENT '用户登录密码',
		`status` INT ( 3 ) NOT NULL COMMENT '用户状态(1:可以使用  0：不可使用)',
		PRIMARY KEY ( `uid` )
	) COMMENT = '用户表' ENGINE = INNODB DEFAULT CHARSET = utf8;

CREATE TABLE
IF
	NOT EXISTS `employee` (
		`eid` VARCHAR ( 255 ) NOT NULL COMMENT '员工id（基于手机号的加密）',
		`nick` VARCHAR ( 50 ) COMMENT '员工昵称',
		`avatar` VARCHAR ( 50 ) COMMENT '头像(上传baseb4)',
		`create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
		`phone` VARCHAR ( 255 ) NOT NULL COMMENT '用户手机号',
		`password` VARCHAR ( 255 ) NOT NULL COMMENT '用户登录密码',
		`status` INT ( 3 ) NOT NULL COMMENT '员工状态(1:可以使用  0：不可使用)',
		PRIMARY KEY ( `eid` )
	) COMMENT = '员工表' ENGINE = INNODB DEFAULT CHARSET = utf8;

CREATE TABLE
IF
	NOT EXISTS `info` (
		`id` INT ( 11 ) AUTO_INCREMENT COMMENT '自增id',
		`uid` VARCHAR ( 255 ) COMMENT '用户id（基于手机号的加密）',
		`title` VARCHAR ( 25 ) NOT NULL COMMENT '标题',
		`name` VARCHAR ( 50 ) COMMENT '姓名',
		`phone` VARCHAR ( 50 ) COMMENT '手机号',
		`create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
		`update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
		`address` VARCHAR ( 255 ) NOT NULL COMMENT '地址',
		`status` INT ( 3 ) NOT NULL COMMENT '信息状态(1:待确认  2：已确认  3：取消)',
		FOREIGN KEY ( `uid` ) REFERENCES users( `uid` ) ON DELETE CASCADE ON UPDATE CASCADE,
		PRIMARY KEY ( `id` )
	) COMMENT = '信息表' ENGINE = INNODB DEFAULT CHARSET = utf8;





