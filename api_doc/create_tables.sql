-- 1. 用户表
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键，用户ID',
  `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `password` varchar(255) NOT NULL COMMENT '密码值',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户表';

-- 2. 演讲室表
CREATE TABLE `speech_rooms` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键，演讲室ID',
  `name` varchar(100) NOT NULL COMMENT '演讲室名称',
  `description` text COMMENT '演讲室描述',
  `creator_id` int NOT NULL COMMENT '创建者用户ID',
  `speaker_id` int DEFAULT NULL COMMENT '演讲者用户ID',
  `invite_code` varchar(20) NOT NULL COMMENT '邀请码（听众使用）',
  `speaker_invite_code` varchar(20) NOT NULL COMMENT '演讲者邀请码',
  `status` tinyint NOT NULL DEFAULT '0' COMMENT '状态：0-等待开始，1-进行中，2-已结束',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_invite_code` (`invite_code`),
  UNIQUE KEY `uk_speaker_invite_code` (`speaker_invite_code`),
  KEY `idx_creator_id` (`creator_id`),
  KEY `idx_speaker_id` (`speaker_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_speech_rooms_creator_id` FOREIGN KEY (`creator_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_speech_rooms_speaker_id` FOREIGN KEY (`speaker_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='演讲室表';

-- 3. 文件上传表
CREATE TABLE `uploaded_files` (
  `id` int NOT NULL AUTO_INCREMENT,
  `filename` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '原始文件名',
  `file_path` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文件存储路径',
  `file_size` bigint NOT NULL COMMENT '文件大小（字节）',
  `file_type` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文件MIME类型',
  `file_extension` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '文件扩展名',
  `uploader_id` int NOT NULL COMMENT '上传者用户ID',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '状态：0-已删除，1-正常',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  PRIMARY KEY (`id`),
  KEY `idx_uploader_id` (`uploader_id`),
  KEY `idx_status` (`status`),
  KEY `idx_file_type` (`file_type`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件上传表';

-- 4. 用户会话表
CREATE TABLE `user_sessions` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` int NOT NULL COMMENT '用户ID，外键',
  `session_token` varchar(255) NOT NULL COMMENT '会话令牌，唯一',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `is_expired` tinyint(1) NOT NULL DEFAULT '0' COMMENT '会话是否过期',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_session_token` (`session_token`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `fk_user_sessions_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户会话表';

-- 5. 用户演讲室参与记录表
CREATE TABLE `user_speech_room_history` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` int NOT NULL COMMENT '用户ID，外键',
  `room_id` int NOT NULL COMMENT '演讲室ID，外键',
  `nickname` varchar(50) DEFAULT NULL COMMENT '用户在演讲室中的昵称',
  `role` tinyint NOT NULL DEFAULT '0' COMMENT '角色：0-创建者，1-演讲者，2-听众',
  `joined_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_room_id` (`room_id`),
  KEY `idx_role` (`role`),
  CONSTRAINT `fk_usrh_room_id` FOREIGN KEY (`room_id`) REFERENCES `speech_rooms` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_usrh_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户演讲室参与记录表';

-- 6. 演讲室在线统计表
CREATE TABLE `speech_room_online` (
  `id` int NOT NULL AUTO_INCREMENT,
  `room_id` int NOT NULL,
  `user_id` int NOT NULL,
  `role` tinyint NOT NULL DEFAULT '2' COMMENT '角色：0-创建者，1-演讲者，2-听众',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_room_user` (`room_id`,`user_id`),
  KEY `idx_room_id` (`room_id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='演讲室在线统计表';

-- 7. 演讲室人员表
CREATE TABLE `speech_room_members` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `room_id` int NOT NULL COMMENT '演讲室ID，外键',
  `user_id` int NOT NULL COMMENT '用户ID，外键',
  `joined_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_room_user` (`room_id`,`user_id`),
  KEY `idx_room_id` (`room_id`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `fk_speech_room_members_room_id` FOREIGN KEY (`room_id`) REFERENCES `speech_rooms` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_speech_room_members_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='演讲室人员表';

-- 8. 演讲室邀请表
CREATE TABLE `speech_room_invitations` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `room_id` int NOT NULL COMMENT '演讲室ID，外键',
  `inviter_id` int NOT NULL COMMENT '邀请人用户ID，外键',
  `invitee_id` int DEFAULT NULL COMMENT '被邀请人用户ID，外键',
  `role` tinyint NOT NULL DEFAULT '0' COMMENT '邀请角色：0-听众，1-演讲者',
  `status` tinyint NOT NULL DEFAULT '0' COMMENT '状态：0-待接受，1-已接受，2-已拒绝，3-已失效',
  `invited_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '邀请创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_room_id` (`room_id`),
  KEY `idx_inviter_id` (`inviter_id`),
  KEY `idx_invitee_id` (`invitee_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_srii_invitee_id` FOREIGN KEY (`invitee_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_srii_inviter_id` FOREIGN KEY (`inviter_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_srii_room_id` FOREIGN KEY (`room_id`) REFERENCES `speech_rooms` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='演讲室邀请表';

-- 9. 原始文本表
CREATE TABLE `raw_texts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `room_id` int NOT NULL COMMENT '产生房间ID，外键',
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '解析得到的原始文本内容',
  `source_type` tinyint NOT NULL DEFAULT '0' COMMENT '来源类型：0-ppt，1-pdf，2-其它',
  `file_id` int DEFAULT NULL COMMENT '关联文件ID，外键',
  `page` int NOT NULL DEFAULT '0' COMMENT '来自文件的页码',
  `used_count` int NOT NULL DEFAULT '0' COMMENT '被用于生成题目的次数',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_room_id` (`room_id`),
  KEY `idx_source_type` (`source_type`),
  KEY `idx_file_id` (`file_id`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='原始文本表';

-- 10. 题目表
CREATE TABLE `questions` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键，题目ID',
  `raw_text` text NOT NULL COMMENT '原始文本',
  `prompt` text NOT NULL COMMENT '提示词',
  `question` varchar(255) DEFAULT NULL COMMENT '问题',
  `option_a` varchar(255) DEFAULT NULL COMMENT '选项A',
  `option_b` varchar(255) DEFAULT NULL COMMENT '选项B',
  `option_c` varchar(255) DEFAULT NULL COMMENT '选项C',
  `option_d` varchar(255) DEFAULT NULL COMMENT '选项D',
  `answer` char(1) DEFAULT NULL COMMENT '正确答案（A/B/C/D）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `created` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否生成完',
  `published` tinyint(1) NOT NULL DEFAULT '0' COMMENT '问题是否被发布过',
  `room_id` int NOT NULL COMMENT '来源演讲室id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='题目表';

-- 11. 被发布题目表
CREATE TABLE `published_questions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `question_id` int NOT NULL COMMENT '原题目ID，外键',
  `room_id` int NOT NULL COMMENT '发布演讲室ID，外键',
  `start_time` datetime DEFAULT NULL COMMENT '答题开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '答题结束时间',
  `time_limit` int DEFAULT '60' COMMENT '答题时间限制（秒）',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '状态：0-进行中，1-已结束',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
  PRIMARY KEY (`id`),
  KEY `idx_question_id` (`question_id`),
  KEY `idx_room_id` (`room_id`),
  KEY `idx_status` (`status`),
  KEY `idx_start_time` (`start_time`),
  KEY `idx_end_time` (`end_time`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='被发布题目表';

-- 12. 答题表
CREATE TABLE `question_answers` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `room_id` int NOT NULL COMMENT '演讲室ID，外键',
  `question_id` int NOT NULL COMMENT '题目ID，外键',
  `user_id` int NOT NULL COMMENT '用户ID，外键',
  `selected_answer` char(1) DEFAULT NULL COMMENT '用户选择的答案（A/B/C/D）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '答题时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_room_question_user` (`room_id`,`question_id`,`user_id`),
  KEY `idx_room_id` (`room_id`),
  KEY `idx_question_id` (`question_id`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `fk_qa_question_id` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_qa_room_id` FOREIGN KEY (`room_id`) REFERENCES `speech_rooms` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_qa_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='答题表';

-- 13. 讨论表
CREATE TABLE `discussions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `room_id` int NOT NULL COMMENT '所属演讲室ID，外键',
  `user_id` int NOT NULL COMMENT '作者用户ID，外键',
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '讨论内容',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `is_system` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否为系统发布',
  `question_id` int NOT NULL DEFAULT '-1' COMMENT '被讨论的题目ID(-1表示不针对题目的讨论)',
  PRIMARY KEY (`id`),
  KEY `idx_room_id` (`room_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_question_id` (`question_id`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='讨论表';