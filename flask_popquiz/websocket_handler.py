from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import json
from datetime import datetime

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
                # 通知房间内其他用户
                emit('user_left', {
                    'user_id': user_id,
                    'username': user_info['username'],
                    'timestamp': datetime.now().isoformat()
                }, room=room_id, include_self=False)
                break

@socketio.on('join_room')
def handle_join_room(data):
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
        emit('new_message', {
            'user_id': user_id,
            'username': username,
            'message': message,
            'timestamp': datetime.now().isoformat()
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