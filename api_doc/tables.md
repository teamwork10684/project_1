# 数据库表设计

## 1. 用户表 (users)

| 字段名     | 数据类型 | 长度 | 是否为空 | 默认值                                        | 说明         |
| ---------- | -------- | ---- | -------- | --------------------------------------------- | ------------ |
| id         | INT      | -    | NOT NULL | AUTO_INCREMENT                                | 主键，用户ID |
| username   | VARCHAR  | 50   | NOT NULL | -                                             | 用户名，唯一 |
| password   | VARCHAR  | 255  | NOT NULL | -                                             | 密码值       |
| created_at | DATETIME | -    | NOT NULL | CURRENT_TIMESTAMP                             | 创建时间     |
| updated_at | DATETIME | -    | NOT NULL | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间     |

**索引：**

- PRIMARY KEY (id)
- UNIQUE KEY (username)

## 2. 用户会话表 (user_sessions)

| 字段名        | 数据类型 | 长度 | 是否为空 | 默认值            | 说明           |
| ------------- | -------- | ---- | -------- | ----------------- | -------------- |
| id            | INT      | -    | NOT NULL | AUTO_INCREMENT    | 主键           |
| user_id       | INT      | -    | NOT NULL | -                 | 用户ID，外键   |
| session_token | VARCHAR  | 255  | NOT NULL | -                 | 会话令牌，唯一 |
| created_at    | DATETIME | -    | NOT NULL | CURRENT_TIMESTAMP | 创建时间       |
| is_expired    | BOOL     |      | NOT NULL | FALSE             | 会话是否过期   |

**索引：**

- PRIMARY KEY (id)
- UNIQUE KEY (session_token)
- INDEX (user_id)

## 3. 演讲室表 (speech_rooms)

| 字段名              | 数据类型 | 长度 | 是否为空 | 默认值                                        | 说明                                 |
| ------------------- | -------- | ---- | -------- | --------------------------------------------- | ------------------------------------ |
| id                  | INT      | -    | NOT NULL | AUTO_INCREMENT                                | 主键，演讲室ID                       |
| name                | VARCHAR  | 100  | NOT NULL | -                                             | 演讲室名称                           |
| description         | TEXT     | -    | NULL     | -                                             | 演讲室描述                           |
| creator_id          | INT      | -    | NOT NULL | -                                             | 创建者用户ID                         |
| speaker_id          | INT      | -    | NULL     | -                                             | 演讲者用户ID                         |
| invite_code         | VARCHAR  | 20   | NOT NULL | -                                             | 邀请码（听众使用，16位随机字符）     |
| speaker_invite_code | VARCHAR  | 20   | NOT NULL | -                                             | 演讲者邀请码（16位随机字符）         |
| status              | TINYINT  | -    | NOT NULL | 0                                             | 状态：0-等待开始，1-进行中，2-已结束 |
| created_at          | DATETIME | -    | NOT NULL | CURRENT_TIMESTAMP                             | 创建时间                             |
| updated_at          | DATETIME | -    | NOT NULL | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间                             |

**索引：**

- PRIMARY KEY (id)
- INDEX (creator_id)
- INDEX (speaker_id)
- INDEX (status)
- UNIQUE KEY (invite_code)
- UNIQUE KEY (speaker_invite_code)

## 4. 演讲室人员表 (speech_room_members)

| 字段名    | 数据类型 | 长度 | 是否为空 | 默认值            | 说明           |
| --------- | -------- | ---- | -------- | ----------------- | -------------- |
| id        | INT      | -    | NOT NULL | AUTO_INCREMENT    | 主键           |
| room_id   | INT      | -    | NOT NULL | -                 | 演讲室ID，外键 |
| user_id   | INT      | -    | NOT NULL | -                 | 用户ID，外键   |
| joined_at | DATETIME | -    | NOT NULL | CURRENT_TIMESTAMP | 加入时间       |

**索引：**

- PRIMARY KEY (id)
- UNIQUE KEY (room_id, user_id)
- INDEX (room_id)
- INDEX (user_id)

## 5. 用户演讲室参与记录表 (user_speech_room_history)

| 字段名    | 数据类型 | 长度 | 是否为空 | 默认值            | 说明                             |
| --------- | -------- | ---- | -------- | ----------------- | -------------------------------- |
| id        | INT      | -    | NOT NULL | AUTO_INCREMENT    | 主键                             |
| user_id   | INT      | -    | NOT NULL | -                 | 用户ID，外键                     |
| room_id   | INT      | -    | NOT NULL | -                 | 演讲室ID，外键                   |
| nickname  | VARCHAR  | 50   | NULL     | -                 | 用户在演讲室中的昵称             |
| role      | TINYINT  | -    | NOT NULL | 0                 | 角色：0-创建者，1-演讲者，2-听众 |
| joined_at | DATETIME | -    | NOT NULL | CURRENT_TIMESTAMP | 加入时间                         |

**索引：**

- PRIMARY KEY (id)
- INDEX (user_id)
- INDEX (room_id)
- INDEX (role)

## 6. 演讲室邀请表 (speech_room_invitations)

| 字段名       | 数据类型 | 长度 | 是否为空 | 默认值            | 说明                                         |
| ------------ | -------- | ---- | -------- | ----------------- | -------------------------------------------- |
| id           | INT      | -    | NOT NULL | AUTO_INCREMENT    | 主键                                         |
| room_id      | INT      | -    | NOT NULL | -                 | 演讲室ID，外键                               |
| inviter_id   | INT      | -    | NOT NULL | -                 | 邀请人用户ID，外键                           |
| invitee_id   | INT      | -    | NULL     | -                 | 被邀请人用户ID，外键                         |
| role         | TINYINT  | -    | NOT NULL | 0                 | 邀请角色：0-听众，1-演讲者                   |
| status       | TINYINT  | -    | NOT NULL | 0                 | 状态：0-待接受，1-已接受，2-已拒绝，3-已失效 |
| invited_time | DATETIME |      | NOT NULL | CURRENT_TIMESTAMP | 邀请创建时间                                 |

**索引：**

- PRIMARY KEY (id)
- INDEX (room_id)
- INDEX (inviter_id)
- INDEX (invitee_id)
- INDEX (status)

## 7. 题目表 (questions)

| 字段名     | 数据类型 | 长度 | 是否为空 | 默认值            | 说明                |
| ---------- | -------- | ---- | -------- | ----------------- | ------------------- |
| id         | INT      | -    | NOT NULL | AUTO_INCREMENT    | 主键，题目ID        |
| room_id    | INT      | -    | NOT NULL | -                 | 来源演讲室id        |
| raw_text   | TEXT     | -    | NOT NULL | -                 | 原始文本            |
| prompt     | TEXT     | -    | NOT NULL | -                 | 提示词              |
| question   | VARCHAR  | 255  | NULL     | -                 | 问题                |
| option_a   | VARCHAR  | 255  | NULL     | -                 | 选项A               |
| option_b   | VARCHAR  | 255  | NULL     | -                 | 选项B               |
| option_c   | VARCHAR  | 255  | NULL     | -                 | 选项C               |
| option_d   | VARCHAR  | 255  | NULL     | -                 | 选项D               |
| answer     | CHAR     | 1    | NULL     | -                 | 正确答案（A/B/C/D） |
| created_at | DATETIME | -    | NOT NULL | CURRENT_TIMESTAMP | 创建时间            |
| created    | BOOL     |      | NOT NULL | FALSE             | 是否生成完          |
| published  | BOOL     |      | NOT NULL | FALSE             | 是否被发布过        |

**索引：**

- PRIMARY KEY (id)

## 8. 答题表 (question_answers)

| 字段名          | 数据类型 | 长度 | 是否为空 | 默认值            | 说明                      |
| --------------- | -------- | ---- | -------- | ----------------- | ------------------------- |
| id              | INT      | -    | NOT NULL | AUTO_INCREMENT    | 主键                      |
| room_id         | INT      | -    | NOT NULL | -                 | 演讲室ID，外键            |
| question_id     | INT      | -    | NOT NULL | -                 | 题目ID，外键              |
| user_id         | INT      | -    | NOT NULL | -                 | 用户ID，外键              |
| selected_answer | CHAR     | 1    | NULL     | -                 | 用户选择的答案（A/B/C/D） |
| created_at      | DATETIME | -    | NOT NULL | CURRENT_TIMESTAMP | 答题时间                  |

**索引：**

- PRIMARY KEY (id)
- INDEX (room_id)
- INDEX (question_id)
- INDEX (user_id)
- UNIQUE KEY (room_id, question_id, user_id)

## 9. 演讲室在线统计表 (speech_room_online)

| 字段名  | 数据类型 | 长度 | 是否为空 | 默认值         | 说明                             |
| ------- | -------- | ---- | -------- | -------------- | -------------------------------- |
| id      | INT      | -    | NOT NULL | AUTO_INCREMENT | 主键                             |
| room_id | INT      | -    | NOT NULL | -              | 演讲室ID，外键                   |
| user_id | INT      | -    | NOT NULL | -              | 用户ID，外键                     |
| role    | TINYINT  | -    | NOT NULL | 2              | 角色：0-创建者，1-演讲者，2-听众 |

**索引：**

- PRIMARY KEY (id)
- UNIQUE KEY (room_id, user_id)
- INDEX (room_id)
- INDEX (user_id)

## 10. 文件上传表 (uploaded_files)

| 字段名         | 数据类型 | 长度 | 是否为空 | 默认值            | 说明                   |
| -------------- | -------- | ---- | -------- | ----------------- | ---------------------- |
| room_id        | INT      | -    | NOT NULL | -                 | 所属演讲室ID，外键     |
| id             | INT      | -    | NOT NULL | AUTO_INCREMENT    | 主键，文件ID           |
| filename       | VARCHAR  | 255  | NOT NULL | -                 | 原始文件名             |
| file_path      | VARCHAR  | 500  | NOT NULL | -                 | 文件存储路径           |
| file_size      | BIGINT   | -    | NOT NULL | -                 | 文件大小（字节）       |
| file_type      | VARCHAR  | 100  | NOT NULL | -                 | 文件MIME类型           |
| file_extension | VARCHAR  | 20   | NULL     | -                 | 文件扩展名             |
| uploader_id    | INT      | -    | NOT NULL | -                 | 上传者用户ID           |
| status         | TINYINT  | -    | NOT NULL | 1                 | 状态：0-已删除，1-正常 |
| created_at     | DATETIME | -    | NOT NULL | CURRENT_TIMESTAMP | 上传时间               |

**索引：**

- PRIMARY KEY (id)
- INDEX (uploader_id)
- INDEX (room_id)
- INDEX (status)
- INDEX (file_type)
- INDEX (created_at)

## 11. 被发布题目表 (published_questions)

每个演讲室发布题目最快频率为五分钟一次(后端检查)

| 字段名      | 数据类型 | 长度 | 是否为空 | 默认值            | 说明                     |
| ----------- | -------- | ---- | -------- | ----------------- | ------------------------ |
| id          | INT      | -    | NOT NULL | AUTO_INCREMENT    | 主键，发布题目ID         |
| question_id | INT      | -    | NOT NULL | -                 | 原题目ID，外键           |
| room_id     | INT      | -    | NOT NULL | -                 | 发布演讲室ID，外键       |
| start_time  | DATETIME | -    | NULL     | -                 | 答题开始时间             |
| end_time    | DATETIME | -    | NULL     | -                 | 答题结束时间             |
| time_limit  | INT      | -    | NULL     | 60                | 答题时间限制（秒）       |
| status      | TINYINT  | -    | NOT NULL | 1                 | 状态：0-进行中，1-已结束 |
| created_at  | DATETIME | -    | NOT NULL | CURRENT_TIMESTAMP | 发布时间                 |

**索引：**

- PRIMARY KEY (id)
- INDEX (question_id)
- INDEX (room_id)
- INDEX (status)
- INDEX (start_time)
- INDEX (end_time)
- INDEX (created_at)

## 12. 原始文本表 (raw_texts)

| 字段名      | 数据类型 | 长度 | 是否为空 | 默认值            | 说明                           |
| ----------- | -------- | ---- | -------- | ----------------- | ------------------------------ |
| id          | INT      | -    | NOT NULL | AUTO_INCREMENT    | 主键，原始文本ID               |
| room_id     | INT      | -    | NOT NULL | -                 | 产生房间ID，外键               |
| content     | TEXT     | -    | NOT NULL | -                 | 解析得到的原始文本内容         |
| source_type | TINYINT  | -    | NOT NULL | 0                 | 来源类型：0-ppt，1-pdf，2-其它 |
| file_id     | INT      | -    | NULL     | -                 | 关联文件ID，外键               |
| page        | INT      | -    | NOT NULL | 0                 | 来自文件的页码                 |
| used_count  | INT      | -    | NOT NULL | 0                 | 被用于生成题目的次数           |
| created_at  | DATETIME | -    | NOT NULL | CURRENT_TIMESTAMP | 创建时间                       |

**索引：**

- PRIMARY KEY (id)
- INDEX (room_id)
- INDEX (creator_id)
- INDEX (source_type)
- INDEX (file_id)
- INDEX (status)
- INDEX (created_at)

## 13. 讨论表 (discussions)

| 字段名      | 数据类型 | 长度 | 是否为空 | 默认值            | 说明                                   |
| ----------- | -------- | ---- | -------- | ----------------- | -------------------------------------- |
| id          | INT      | -    | NOT NULL | AUTO_INCREMENT    | 主键，讨论ID                           |
| room_id     | INT      | -    | NOT NULL | -                 | 所属演讲室ID，外键                     |
| user_id     | INT      | -    | NOT NULL | -                 | 作者用户ID，外键                       |
| content     | TEXT     | -    | NOT NULL | -                 | 讨论内容                               |
| created_at  | DATETIME | -    | NOT NULL | CURRENT_TIMESTAMP | 创建时间                               |
| is_system   | BOOL     | -    | NOT NULL | FALSE             | 是否为系统发布                         |
| question_id | INT      | -    | NOT NULL | -1                | 被讨论的题目ID(-1表示不针对题目的讨论) |

**索引：**

- PRIMARY KEY (id)
- INDEX (room_id)
- INDEX (author_id)
- INDEX (parent_id)
- INDEX (type)
- INDEX (status)
- INDEX (is_pinned)
- INDEX (created_at)
