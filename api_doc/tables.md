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
| invite_code         | VARCHAR  | 20   | NOT NULL | -                                             | 邀请号（听众使用）                   |
| speaker_invite_code | VARCHAR  | 20   | NOT NULL | -                                             | 演讲者邀请号                         |
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
| closed     | BOOL     |      | NOT NULL | FALSE             | 回答是否结束        |

**索引：**

- PRIMARY KEY (id)

## 8. 演讲室题目关联表 (speech_room_questions)

| 字段名      | 数据类型 | 长度 | 是否为空 | 默认值         | 说明                       |
| ----------- | -------- | ---- | -------- | -------------- | -------------------------- |
| id          | INT      | -    | NOT NULL | AUTO_INCREMENT | 主键                       |
| room_id     | INT      | -    | NOT NULL | -              | 演讲室ID，外键             |
| question_id | INT      | -    | NOT NULL | -              | 题目ID，外键               |
| sort_order  | INT      | -    | NOT NULL | 0              | 用于同一个演讲室的题目排序 |

**索引：**

- PRIMARY KEY (id)
- INDEX (room_id)
- INDEX (question_id)
- UNIQUE KEY (room_id, question_id)

## 9. 答题表 (question_answers)

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
