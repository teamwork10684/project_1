from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from datetime import datetime
from models import db
from models.speech_room_online import SpeechRoomOnline
from models.discussion import Discussion

socketio = SocketIO(cors_allowed_origins="*")

# 存储房间内的用户连接信息
room_connections = {}  # {room_id: {user_id: {'sid': sid, 'username': username, 'role': role}}}

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    # 清理断开连接的用户
    for room_id, users in room_connections.items():
        for user_id, user_info in list(users.items()):
            if user_info['sid'] == request.sid:
                del users[user_id]
                # 新增：从SpeechRoomOnline表删除
                try:
                    SpeechRoomOnline.query.filter_by(room_id=room_id, user_id=user_id).delete()
                    db.session.commit()
                except Exception as e:
                    print(f"[WebSocket] SpeechRoomOnline delete error: {e}")
                # 通知房间内其他用户
                emit('user_left', {
                    'user_id': user_id,
                    'username': user_info['username'],
                    'timestamp': datetime.now().isoformat()
                }, room=room_id, include_self=False)
                break

@socketio.on('join_room')
def handle_join_room(data):
    print(f"[WebSocket] join_room: {data}")
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    username = data.get('username')
    role = data.get('role')
    
    if not all([room_id, user_id, username]):
        return
    
    # 加入房间
    join_room(room_id)
    
    # 记录用户连接信息
    if room_id not in room_connections:
        room_connections[room_id] = {}
    
    room_connections[room_id][user_id] = {
        'sid': request.sid,
        'username': username,
        'role': role,
        'joined_at': datetime.now().isoformat()
    }
    
    # 新增：添加到SpeechRoomOnline表
    try:
        exist = SpeechRoomOnline.query.filter_by(room_id=room_id, user_id=user_id).first()
        if not exist:
            online = SpeechRoomOnline(room_id=room_id, user_id=user_id, role=role)
            db.session.add(online)
            db.session.commit()
    except Exception as e:
        print(f"[WebSocket] SpeechRoomOnline add error: {e}")
    
    # 通知房间内其他用户有新用户加入
    emit('user_joined', {
        'user_id': user_id,
        'username': username,
        'role': role,
        'timestamp': datetime.now().isoformat()
    }, room=room_id, include_self=False)
    
    # 向新用户发送当前房间内的用户列表
    current_users = []
    for uid, user_info in room_connections[room_id].items():
        current_users.append({
            'user_id': uid,
            'username': user_info['username'],
            'role': user_info['role']
        })
    
    emit('room_users', {
        'users': current_users,
        'total_online': len(current_users)
    })

@socketio.on('leave_room')
def handle_leave_room(data):
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    
    if room_id and user_id:
        leave_room(room_id)
        
        # 从房间连接记录中移除用户
        if room_id in room_connections and user_id in room_connections[room_id]:
            user_info = room_connections[room_id][user_id]
            del room_connections[room_id][user_id]
            
            # 新增：从SpeechRoomOnline表删除
            try:
                SpeechRoomOnline.query.filter_by(room_id=room_id, user_id=user_id).delete()
                db.session.commit()
            except Exception as e:
                print(f"[WebSocket] SpeechRoomOnline delete error: {e}")
            
            # 通知房间内其他用户
            emit('user_left', {
                'user_id': user_id,
                'username': user_info['username'],
                'timestamp': datetime.now().isoformat()
            }, room=room_id, include_self=False)

@socketio.on('send_message')
def handle_send_message(data):
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    username = data.get('username')
    message = data.get('message')
    
    if all([room_id, user_id, username, message]):
        # 新增：判断当前房间有无进行中的题目
        from models.published_question import PublishedQuestion
        question_id = -1
        try:
            published = PublishedQuestion.query.filter_by(room_id=room_id, status=0).first()
            if published:
                question_id = published.question_id
        except Exception as e:
            print(f"[WebSocket] 查询进行中题目出错: {e}")
        # 新增：插入到Discussion表
        try:
            discussion = Discussion(
                room_id=room_id,
                user_id=user_id,
                content=message,
                is_system=False,
                question_id=question_id
            )
            db.session.add(discussion)
            db.session.commit()
        except Exception as e:
            print(f"[WebSocket] Discussion insert error: {e}")
        emit('new_message', {
            'user_id': user_id,
            'username': username,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'is_system': False
        }, room=room_id)

def get_room_online_count(room_id):
    """获取房间在线人数"""
    if room_id in room_connections:
        return len(room_connections[room_id])
    return 0

def get_room_participants(room_id):
    """获取房间参与者列表"""
    if room_id in room_connections:
        participants = []
        for user_id, user_info in room_connections[room_id].items():
            participants.append({
                'user_id': user_id,
                'username': user_info['username'],
                'role': user_info['role']
            })
        return participants
    return [] 