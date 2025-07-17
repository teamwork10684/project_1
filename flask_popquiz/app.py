from flask import Flask, request, jsonify
import ollama
from flask_cors import CORS
from module.aifilter.aifilter import filter_markdown
from models import db, User, UserSession, SpeechRoom, SpeechRoomMember, SpeechRoomInvitation, Question,QuestionAnswer, SpeechRoomOnline, Discussion, PublishedQuestion
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy import text
from websocket_handler import socketio

app = Flask(__name__)
CORS(app, supports_credentials=True)
socketio.init_app(app, cors_allowed_origins="*")

OLLAMA_MODEL = 'deepseek-r1:7b'

# SQLAlchemy配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:7661282cjyCJY@localhost:3306/popquiz?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/popquiz/getQuestionByTextOllamaDemo', methods=['POST'])
def get_question_by_text_demo():
    data = request.get_json()
    original_prompt = data.get('original_prompt', '').strip()
    if not original_prompt:
        return jsonify({'message': '参数 original_prompt 不能为空'}), 400
    prompt = (
        "你是一名专业的教育内容生成AI，请根据用户提供的原始文本内容，生成一道单项选择题。"
        "请严格按照以下要求输出：\n"
        "1. 题目内容应与原始文本高度相关，简明扼要，问题长度尽可能地短。\n"
        "2. 只生成一道题目。\n"
        "3. 只输出JSON格式，包含三个字段：question（字符串，题目内容），options（字符串数组，长度为4，4个选项）,answer(A、B、C、D中的一个，只需要给出对应选项字母，不用重复选项内容!!!)。\n"
        "4. 选项内容应合理且互不重复，只有一个正确答案，其余为干扰项。\n"
        "5. 不要输出除JSON以外的任何内容。\n"
        "6. JSON示例{\"question\":\"问题\",\"options\":[\"选项A\",\"选项B\",\"选项C\",\"选项D\"],\"answer\":\"A\"}\n"
        f"原始文本：{original_prompt}"
        "注意！除了返回json格式的回答外不要返回任何其他内容！！！"
    )
    try:
        print(original_prompt)
        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            stream=False,
            think=False
        )
        import json as pyjson
        response_text = response.get('response', '')
        response_text = filter_markdown(response_text)
        print(response_text)
        try:
            data = pyjson.loads(response_text)
            question = data.get('question')
            options = data.get('options')
            answer = data.get('answer')
            if not question or not isinstance(options, list) or len(options) != 4 or answer not in ['A', 'B', 'C', 'D']:
                raise ValueError('AI返回格式不正确')
            # 随机打乱选项并更新答案
            import random
            option_map = list(zip(['A', 'B', 'C', 'D'], options))
            random.shuffle(option_map)
            shuffled_options = [opt for _, opt in option_map]
            # 找到原答案对应的内容
            original_answer_content = options[ord(answer) - ord('A')]
            # 新的answer字母
            for idx, (_, opt) in enumerate(option_map):
                if opt == original_answer_content:
                    new_answer = chr(ord('A') + idx)
                    break
            else:
                new_answer = None
            return jsonify({'question': question, 'options': shuffled_options, 'answer': new_answer})
        except Exception:
            return jsonify({'message': 'AI返回内容解析失败', 'raw': response_text}), 400
    except Exception as e:
        return jsonify({'message': f'AI服务异常: {str(e)}'}), 500

# 用户注册
@app.route('/popquiz/register', methods=['POST'])
def register():
    """用户注册账号"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'message': '参数错误'}), 400
    # 检查用户名唯一性
    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 400
    # 明文保存密码
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': f'user_{user.id}', 'message': '注册成功'}), 201

# 用户登录
@app.route('/popquiz/login', methods=['POST'])
def login():
    """用户登录系统，返回身份信息和 token"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'message': '参数错误'}), 400
    user = User.query.filter_by(username=username).first()
    if not user or user.password != password:
        return jsonify({'message': '用户名或密码错误'}), 401
    # 生成token
    from sqlalchemy.exc import IntegrityError
    
    max_retries = 10
    for attempt in range(max_retries):
        try:
            token = str(uuid.uuid4())
            # 标记旧session为过期（支持多设备登录）
            db.session.execute(text("UPDATE user_sessions SET is_expired = 1 WHERE user_id = :uid"), {"uid": user.id})
            # 插入新session
            db.session.execute(text("INSERT INTO user_sessions (user_id, session_token, created_at, is_expired) VALUES (:uid, :token, :created_at, 0)"), {
                "uid": user.id,
                "token": token,
                "created_at": datetime.now()
            })
            db.session.commit()
            break  # 成功插入，跳出循环
            
        except IntegrityError:
            # token重复，回滚并重试
            db.session.rollback()
            if attempt == max_retries - 1:
                return jsonify({'message': '登录失败，请重试'}), 500
            continue
    return jsonify({'token': token, 'message': '登录成功'}), 200

# 创建演讲室
@app.route('/popquiz/speech-rooms', methods=['POST'])
def create_speech_room():
    """用户创建新的演讲室"""
    data = request.get_json()
    token = data.get('session_token', '').strip()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip() if data.get('description') else None
    is_speaker = data.get('is_speaker', False)
    if not token or not name:
        return jsonify({'message': '参数错误'}), 400
    # 校验token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    creator_id = session.user_id
    # 生成邀请码
    import random, string
    from sqlalchemy.exc import IntegrityError
    def gen_code():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    # 使用重试机制确保生成唯一邀请码
    max_retries = 10
    
    for attempt in range(max_retries):
        try:
            invite_code = gen_code()
            speaker_invite_code = gen_code()
            
            # 插入房间
            room = SpeechRoom(
                name=name,
                description=description,
                creator_id=creator_id,
                speaker_id=creator_id if is_speaker else None,
                invite_code=invite_code,
                speaker_invite_code=speaker_invite_code,
                status=0
            )
            db.session.add(room)
            db.session.commit()
            break  # 成功插入，跳出循环
            
        except IntegrityError:
            # 邀请码重复，回滚并重试
            db.session.rollback()
            if attempt == max_retries - 1:
                return jsonify({'message': '生成邀请码失败，请重试'}), 500
            continue
    # 创建者自动加入房间
    member = SpeechRoomMember(room_id=room.id, user_id=creator_id)
    db.session.add(member)
    db.session.commit()
    return jsonify({
        'id': room.id,
        'name': room.name,
        'description': room.description,
        'creator_id': room.creator_id,
        'speaker_id': room.speaker_id,
        'invite_code': room.invite_code,
        'speaker_invite_code': room.speaker_invite_code,
        'status': room.status,
        'created_at': room.created_at.isoformat(),
        'message': '演讲室创建成功'
    }), 201

# 用户退出登录
@app.route('/popquiz/logout', methods=['POST'])
def logout():
    """用户主动退出登录，令牌失效"""
    data = request.get_json()
    token = data.get('token', '').strip()
    if not token:
        return jsonify({'message': '参数错误'}), 400
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    # 标记session为过期
    session.is_expired = True
    db.session.commit()
    return jsonify({'message': '退出成功'}), 200

# 获取用户参与的所有演讲室
@app.route('/popquiz/user/speech-rooms', methods=['GET'])
def get_user_speech_rooms():
    """获取当前用户参与或创建的所有演讲室列表"""
    token = request.args.get('token', '').strip()
    if not token:
        return jsonify({'message': '参数错误'}), 400
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    user_id = session.user_id
    # 参与的
    member_rooms = SpeechRoomMember.query.filter_by(user_id=user_id).all()
    room_ids = [m.room_id for m in member_rooms]
    rooms = SpeechRoom.query.filter(SpeechRoom.id.in_(room_ids)).all() if room_ids else []
    # 创建的
    created_rooms = SpeechRoom.query.filter_by(creator_id=user_id).all()
    all_rooms = {r.id: r for r in rooms + created_rooms}
    result = []
    for r in all_rooms.values():
        # 获取参与人数
        participant_count = SpeechRoomMember.query.filter_by(room_id=r.id).count()
        
        # 获取创始人姓名
        creator = User.query.get(r.creator_id)
        creator_name = creator.username if creator else None
        
        # 获取演讲人姓名
        speaker_name = None
        if r.speaker_id:
            speaker = User.query.get(r.speaker_id)
            speaker_name = speaker.username if speaker else None
        
        # 确定用户角色
        if r.creator_id == user_id:
            role = 0  # 创建者
            # 创建者可以看到邀请码
            invite_code = r.invite_code
            speaker_invite_code = r.speaker_invite_code
        elif r.speaker_id == user_id:
            role = 1  # 演讲者
            # 非创建者看不到邀请码
            invite_code = None
            speaker_invite_code = None
        else:
            role = 2  # 听众
            # 非创建者看不到邀请码
            invite_code = None
            speaker_invite_code = None
        
        result.append({
            'id': r.id,
            'name': r.name,
            'description': r.description,
            'creator_id': r.creator_id,
            'speaker_id': r.speaker_id,
            'role': role,
            'invite_code': invite_code,
            'speaker_invite_code': speaker_invite_code,
            'status': r.status,
            'created_at': r.created_at.isoformat() if r.created_at else None,
            'total_participants': participant_count,
            'creator_name': creator_name,
            'speaker_name': speaker_name
        })
    return jsonify({'rooms': result}), 200

# 获取用户所有被邀请记录
@app.route('/popquiz/user/invitations', methods=['GET'])
def get_user_invitations():
    """获取当前用户所有的被邀请记录"""
    token = request.args.get('token', '').strip()
    if not token:
        return jsonify({'message': '参数错误'}), 400
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    user_id = session.user_id
    invitations = SpeechRoomInvitation.query.filter_by(invitee_id=user_id).all()
    result = []
    for inv in invitations:
        # 获取房间信息
        room = SpeechRoom.query.get(inv.room_id)
        if not room:
            continue
            
        # 获取组织者信息
        creator = User.query.get(room.creator_id)
        creator_name = creator.username if creator else None
        
        # 获取演讲者信息
        speaker_name = None
        if room.speaker_id:
            speaker = User.query.get(room.speaker_id)
            speaker_name = speaker.username if speaker else None
        
        # 获取参与人数
        participant_count = SpeechRoomMember.query.filter_by(room_id=room.id).count()
        
        result.append({
            'id': inv.id,
            'room_id': room.id,
            'room_name': room.name,
            'description': room.description,
            'created_at': room.created_at.isoformat() if room.created_at else None,
            'creator_name': creator_name,
            'speaker_name': speaker_name,
            'total_participants': participant_count,
            'role': inv.role,
            'status': inv.status,
            'room_status': room.status,
            'invited_time': inv.invited_time.isoformat() if inv.invited_time else None
        })
    return jsonify({'invitations': result}), 200

# 发起邀请
@app.route('/popquiz/invitations', methods=['POST'])
def invite_user():
    """由发起人邀请其他用户加入演讲室"""
    data = request.get_json()
    token = data.get('token', '').strip()
    invitee_username = data.get('invitee_username', '').strip()
    room_id = data.get('room_id')
    role = data.get('role')
    if not token or not invitee_username or room_id is None or role is None:
        return jsonify({'message': '参数错误'}), 400
    # 校验发起人token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    inviter_id = session.user_id
    # 校验被邀请用户
    invitee = User.query.filter_by(username=invitee_username).first()
    if not invitee:
        return jsonify({'message': '被邀请用户不存在'}), 400
    invitee_id = invitee.id
    
    # 检查不能邀请自己
    if invitee_id == inviter_id:
        return jsonify({'message': '不能邀请自己'}), 400
    
    # 校验房间存在
    room = SpeechRoom.query.get(room_id)
    if not room:
        return jsonify({'message': '演讲室不存在'}), 400
    
    # 检查房间状态（0-等待开始，1-进行中，2-已结束）
    if room.status != 0:
        if room.status == 1 and role == 1:
            return jsonify({'message': '房间已开始，无法发送演讲者邀请'}), 400
        elif room.status == 2:
            return jsonify({'message': '房间已结束，无法发送邀请'}), 400
    
    # 检查是否为房间创建者
    if room.creator_id != inviter_id:
        return jsonify({'message': '只有房间创建者才能发送邀请'}), 403
    
    # 检查角色值是否有效
    if role not in [0, 1]:  # 0-听众，1-演讲者
        return jsonify({'message': '无效的角色值'}), 400
    
    # 检查是否邀请演讲者角色
    if role == 1:  # 1表示演讲者角色
        # 检查房间是否已有演讲者
        if room.speaker_id is not None:
            return jsonify({'message': '该演讲室已有演讲者，无法再邀请演讲者'}), 400
    
    # 检查被邀请用户是否已加入房间
    exist_member = SpeechRoomMember.query.filter_by(room_id=room_id, user_id=invitee_id).first()
    if exist_member:
        return jsonify({'message': '该用户已加入房间'}), 400
    
    # 检查是否已存在邀请（包括所有状态的邀请）
    exist_invitation = SpeechRoomInvitation.query.filter_by(
        room_id=room_id, 
        invitee_id=invitee_id, 
        role=role
    ).first()
    if exist_invitation:
        if exist_invitation.status == 0:
            return jsonify({'id': exist_invitation.id, 'message': '邀请已存在'}), 201
        elif exist_invitation.status == 1:
            return jsonify({'message': '该用户已接受过相同邀请'}), 400
        elif exist_invitation.status == 2:
            # 如果邀请被拒绝，删除旧邀请记录，允许重新发送
            db.session.delete(exist_invitation)
            db.session.commit()
    # 插入邀请
    invitation = SpeechRoomInvitation(
        room_id=room_id,
        inviter_id=inviter_id,
        invitee_id=invitee_id,
        role=role,
        status=0
    )
    db.session.add(invitation)
    db.session.commit()
    return jsonify({'id': invitation.id, 'message': '邀请已发送'}), 201

# 接受邀请
@app.route('/popquiz/invitations/accept', methods=['POST'])
def accept_invitation():
    """用户接受某条邀请"""
    data = request.get_json()
    invitation_id = data.get('id')
    token = data.get('token', '').strip()
    if invitation_id is None or not token:
        return jsonify({'message': '参数错误'}), 400
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    user_id = session.user_id
    invitation = SpeechRoomInvitation.query.get(invitation_id)
    if not invitation or invitation.status != 0:
        return jsonify({'message': '邀请已处理或已失效'}), 400
    if invitation.invitee_id != user_id:
        return jsonify({'message': '无权操作该邀请'}), 403
    room_id = invitation.room_id
    role = invitation.role
    
    # 检查房间状态，不能加入已结束的房间
    room = SpeechRoom.query.get(room_id)
    if not room:
        return jsonify({'message': '演讲室不存在'}), 400
    if room.status == 2:
        return jsonify({'message': '房间已结束，无法接受邀请'}), 400
    
    # 更新邀请状态为已接受
    invitation.status = 1
    # 如果是演讲者，更新房间表的speaker_id
    if role == 1:
        if room:
            room.speaker_id = user_id
    # 插入成员记录（如未存在）
    exist_member = SpeechRoomMember.query.filter_by(room_id=room_id, user_id=user_id).first()
    if not exist_member:
        member = SpeechRoomMember(room_id=room_id, user_id=user_id)
        db.session.add(member)
    db.session.commit()
    return jsonify({'id': invitation_id, 'message': '邀请已接受'}), 200

# 拒绝邀请
@app.route('/popquiz/invitations/reject', methods=['POST'])
def reject_invitation():
    """用户拒绝某条邀请"""
    data = request.get_json()
    invitation_id = data.get('id')
    token = data.get('token', '').strip()
    if invitation_id is None or not token:
        return jsonify({'message': '参数错误'}), 400
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    user_id = session.user_id
    invitation = SpeechRoomInvitation.query.get(invitation_id)
    if not invitation or invitation.status != 0:
        return jsonify({'message': '邀请已处理或已失效'}), 400
    if invitation.invitee_id != user_id:
        return jsonify({'message': '无权操作该邀请'}), 403
    invitation.status = 2  # 拒绝
    db.session.commit()
    return jsonify({'id': invitation_id, 'message': '邀请已拒绝'}), 200

# 加入演讲室
@app.route('/popquiz/join-room', methods=['POST'])
def join_room():
    """用户通过邀请码加入演讲室"""
    data = request.get_json()
    token = data.get('token', '').strip()
    invite_code = data.get('invite_code', '').strip()
    if not token or not invite_code:
        return jsonify({'message': '参数错误'}), 400
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    user_id = session.user_id
    
    # 判断邀请码类型并查找房间
    is_speaker_invite = False
    room = SpeechRoom.query.filter_by(invite_code=invite_code).first()
    if not room:
        room = SpeechRoom.query.filter_by(speaker_invite_code=invite_code).first()
        if room:
            is_speaker_invite = True
    
    if not room:
        return jsonify({'message': '邀请码无效'}), 400
    
    # 检查房间状态，不能加入已结束的房间
    if room.status == 2:
        return jsonify({'message': '房间已结束，无法加入'}), 400
    
    # 如果是演讲者邀请码，检查房间是否已有演讲者
    if is_speaker_invite:
        if room.speaker_id is not None:
            return jsonify({'message': '该演讲室已有演讲者'}), 400
    
    # 检查是否已加入
    exist = SpeechRoomMember.query.filter_by(room_id=room.id, user_id=user_id).first()
    if exist:
        return jsonify({'message': '已加入过该房间'}), 400
    
    # 如果是演讲者邀请码，更新房间的演讲者ID
    if is_speaker_invite:
        room.speaker_id = user_id
    
    member = SpeechRoomMember(room_id=room.id, user_id=user_id)
    db.session.add(member)
    db.session.commit()
    return jsonify({'room_id': room.id, 'message': '加入成功'}), 200

# 开始演讲
@app.route('/popquiz/speech-rooms/<int:room_id>/start', methods=['POST'])
def start_speech(room_id):
    """房间创建者或演讲者开始演讲"""
    data = request.get_json()
    token = data.get('token', '').strip()
    if not token:
        return jsonify({'message': '参数错误'}), 400
    
    # 校验token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    
    user_id = session.user_id
    
    # 查找房间
    room = SpeechRoom.query.get(room_id)
    if not room:
        return jsonify({'message': '演讲室不存在'}), 404
    
    # 检查权限：只有房间创建者和演讲者才能开始演讲
    if room.creator_id != user_id and room.speaker_id != user_id:
        return jsonify({'message': '只有房间创建者和演讲者才能开始演讲'}), 403
    
    # 检查房间状态：只有等待开始(0)的房间才能开始演讲
    if room.status != 0:
        return jsonify({'message': '房间状态不允许开始演讲'}), 400
    
    # 如果房间没有演讲人，自动将组织者设为演讲人
    if room.speaker_id is None:
        room.speaker_id = room.creator_id
    
    # 更新房间状态为进行中(1)
    room.status = 1
    db.session.commit()
    
    return jsonify({
        'room_id': room.id,
        'status': room.status,
        'speaker_id': room.speaker_id,
        'message': '演讲已开始'
    }), 200

# 结束演讲
@app.route('/popquiz/speech-rooms/<int:room_id>/end', methods=['POST'])
def end_speech(room_id):
    """房间创建者或演讲者结束演讲"""
    data = request.get_json()
    token = data.get('token', '').strip()
    if not token:
        return jsonify({'message': '参数错误'}), 400
    
    # 校验token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    
    user_id = session.user_id
    
    # 查找房间
    room = SpeechRoom.query.get(room_id)
    if not room:
        return jsonify({'message': '演讲室不存在'}), 404
    
    # 检查权限：只有房间创建者和演讲者才能结束演讲
    if room.creator_id != user_id and room.speaker_id != user_id:
        return jsonify({'message': '只有房间创建者和演讲者才能结束演讲'}), 403
    
    # 检查房间状态：只有进行中(1)的房间才能结束演讲
    if room.status != 1:
        return jsonify({'message': '房间状态不允许结束演讲'}), 400
    
    # 更新房间状态为已结束(2)
    room.status = 2
    db.session.commit()
    
    return jsonify({
        'room_id': room.id,
        'status': room.status,
        'message': '演讲已结束'
    }), 200

# 获取演讲室参与总人数
@app.route('/popquiz/speech-rooms/<int:room_id>/participants/count', methods=['GET'])
def get_room_participants_count(room_id):
    """获取指定演讲室的参与人数统计"""
    token = request.args.get('token', '').strip()
    if not token:
        return jsonify({'message': '参数错误'}), 400
    
    # 校验token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    
    # 查找房间
    room = SpeechRoom.query.get(room_id)
    if not room:
        return jsonify({'message': '演讲室不存在'}), 404
    
    # 统计参与人数
    participant_count = SpeechRoomMember.query.filter_by(room_id=room_id).count()
    
    return jsonify({
        'room_id': room.id,
        'total_participants': participant_count,
        'creator_id': room.creator_id,
        'speaker_id': room.speaker_id,
        'message': '获取成功'
    }), 200

# 获取演讲室在线人员列表
@app.route('/popquiz/speech-rooms/<int:room_id>/online-participants', methods=['GET'])
def get_room_online_participants(room_id):
    """获取指定演讲室的所有在线人员信息"""
    token = request.args.get('token', '').strip()
    if not token:
        return jsonify({'message': '参数错误'}), 400
    
    # 校验token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    
    user_id = session.user_id
    
    # 查找房间
    room = SpeechRoom.query.get(room_id)
    if not room:
        return jsonify({'message': '演讲室不存在'}), 404
    
    # 检查用户是否为该演讲室的成员
    member = SpeechRoomMember.query.filter_by(room_id=room_id, user_id=user_id).first()
    if not member:
        return jsonify({'message': '您不是该演讲室的成员'}), 403
    
    # 从演讲室在线统计表获取在线人员
    online_users = SpeechRoomOnline.query.filter_by(room_id=room_id).all()
    
    participants = []
    for online_user in online_users:
        # 获取用户信息
        user = User.query.get(online_user.user_id)
        if not user:
            continue
        
        participants.append({
            'user_id': online_user.user_id,
            'username': user.username,
            'role': online_user.role
        })
    
    return jsonify({
        'room_id': room.id,
        'room_name': room.name,
        'total_online': len(participants),
        'participants': participants,
        'message': '获取在线人员列表成功'
    }), 200

# 进入房间获取房间信息和角色信息
@app.route('/popquiz/speech-rooms/<int:room_id>/enter', methods=['GET'])
def enter_room_and_get_info(room_id):
    """进入房间获取房间信息和用户在指定演讲室中扮演的角色"""
    token = request.args.get('token', '').strip()
    if not token:
        return jsonify({'message': '参数错误'}), 400
    
    # 校验token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    
    user_id = session.user_id
    
    # 查找房间
    room = SpeechRoom.query.get(room_id)
    if not room:
        return jsonify({'message': '演讲室不存在'}), 404
    
    # 检查用户是否为该演讲室的成员
    member = SpeechRoomMember.query.filter_by(room_id=room_id, user_id=user_id).first()
    if not member:
        return jsonify({'message': '您不是该演讲室的成员'}), 403
    
    # 获取用户信息
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    # 获取创建者信息
    creator = User.query.get(room.creator_id)
    creator_name = creator.username if creator else None
    
    # 获取演讲者信息
    speaker_name = None
    if room.speaker_id:
        speaker = User.query.get(room.speaker_id)
        speaker_name = speaker.username if speaker else None
    
    # 统计参与人数
    participant_count = SpeechRoomMember.query.filter_by(room_id=room_id).count()
    
    # 确定用户角色
    if room.creator_id == user_id:
        role = 0  # 创建者
    elif room.speaker_id == user_id:
        role = 1  # 演讲者
    else:
        role = 2  # 听众
    
    return jsonify({
        'room_info': {
            'id': room.id,
            'name': room.name,
            'description': room.description,
            'creator_id': room.creator_id,
            'creator_name': creator_name,
            'speaker_id': room.speaker_id,
            'speaker_name': speaker_name,
            'status': room.status,
            'total_participants': participant_count,
            'created_at': room.created_at.isoformat() if room.created_at else None
        },
        'user_info': {
            'user_id': user_id,
            'username': user.username,
            'role': role
        },
        'message': '进入房间成功'
    }), 200

# 获取用户创建的所有演讲室
@app.route('/popquiz/user/created-rooms', methods=['GET'])
def get_user_created_rooms():
    """获取当前用户作为创建者的所有演讲室列表"""
    token = request.args.get('token', '').strip()
    if not token:
        return jsonify({'message': '参数错误'}), 400
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 100)  # 限制每页最大数量
    
    # 获取排序参数
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')
    
    # 获取状态过滤参数
    status_filter = request.args.get('status', type=int)
    
    # 验证排序字段
    valid_sort_fields = ['created_at', 'name', 'status']
    if sort_by not in valid_sort_fields:
        sort_by = 'created_at'
    
    # 验证排序方向
    if order not in ['asc', 'desc']:
        order = 'desc'
    
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    
    user_id = session.user_id
    
    try:
        # 构建查询
        query = SpeechRoom.query.filter_by(creator_id=user_id)
        
        # 添加状态过滤
        if status_filter is not None:
            query = query.filter_by(status=status_filter)
        
        # 添加排序
        if sort_by == 'created_at':
            if order == 'desc':
                query = query.order_by(SpeechRoom.created_at.desc())
            else:
                query = query.order_by(SpeechRoom.created_at.asc())
        elif sort_by == 'name':
            if order == 'desc':
                query = query.order_by(SpeechRoom.name.desc())
            else:
                query = query.order_by(SpeechRoom.name.asc())
        elif sort_by == 'status':
            if order == 'desc':
                query = query.order_by(SpeechRoom.status.desc())
            else:
                query = query.order_by(SpeechRoom.status.asc())
        
        # 执行分页查询
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        rooms = pagination.items
        
        result = []
        for r in rooms:
            if r.id is None:  # 跳过无效数据
                continue
            result.append({
                'id': r.id,
                'name': r.name,
                'description': r.description,
                'creator_id': r.creator_id,
                'speaker_id': r.speaker_id,
                'invite_code': r.invite_code,
                'speaker_invite_code': r.speaker_invite_code,
                'status': r.status,
                'created_at': r.created_at.isoformat() if r.created_at else None
            })
        
        response_data = {
            'rooms': result,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
        
        response = jsonify(response_data)
        response.headers['Cache-Control'] = 'no-cache'
        return response, 200
        
    except Exception as e:
        return jsonify({'message': '查询失败'}), 500

# 发表讨论
@app.route('/popquiz/discussions', methods=['POST'])
def create_discussion():
    """用户在指定演讲室发表讨论内容"""
    data = request.get_json()
    token = data.get('token', '').strip()
    room_id = data.get('room_id')
    content = data.get('content', '').strip()
    question_id = data.get('question_id', -1)
    
    if not token or room_id is None or not content:
        return jsonify({'message': '参数错误'}), 400
    
    # 校验token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    
    user_id = session.user_id
    
    # 查找房间
    room = SpeechRoom.query.get(room_id)
    if not room:
        return jsonify({'message': '演讲室不存在'}), 404
    
    # 检查用户是否为该演讲室的成员
    member = SpeechRoomMember.query.filter_by(room_id=room_id, user_id=user_id).first()
    if not member:
        return jsonify({'message': '您不是该演讲室的成员'}), 403
    
    # 如果指定了题目ID，检查题目是否存在
    if question_id != -1:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'message': '指定的题目不存在'}), 404
    
    # 创建讨论记录
    discussion = Discussion(
        room_id=room_id,
        user_id=user_id,
        content=content,
        question_id=question_id,
        is_system=False
    )
    
    db.session.add(discussion)
    db.session.commit()
    
    return jsonify({
        'id': discussion.id,
        'room_id': discussion.room_id,
        'user_id': discussion.user_id,
        'content': discussion.content,
        'question_id': discussion.question_id,
        'created_at': discussion.created_at.isoformat(),
        'message': '讨论发表成功'
    }), 201

# 获取讨论列表
@app.route('/popquiz/discussions', methods=['GET'])
def get_discussions():
    """获取指定演讲室的讨论列表"""
    room_id = request.args.get('room_id', type=int)
    token = request.args.get('token', '').strip()
    
    if not room_id or not token:
        return jsonify({'message': '参数错误'}), 400
    
    # 校验token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    
    user_id = session.user_id
    
    # 查找房间
    room = SpeechRoom.query.get(room_id)
    if not room:
        return jsonify({'message': '演讲室不存在'}), 404
    
    # 检查用户是否为该演讲室的成员
    member = SpeechRoomMember.query.filter_by(room_id=room_id, user_id=user_id).first()
    if not member:
        return jsonify({'message': '您不是该演讲室的成员'}), 403
    
    # 获取讨论列表
    discussions = Discussion.query.filter_by(room_id=room_id).order_by(Discussion.created_at.desc()).all()
    
    result = []
    for discussion in discussions:
        # 获取用户信息
        user = User.query.get(discussion.user_id)
        username = user.username if user else '未知用户'
        
        result.append({
            'id': discussion.id,
            'room_id': discussion.room_id,
            'user_id': discussion.user_id,
            'username': username,
            'content': discussion.content,
            'question_id': discussion.question_id,
            'is_system': discussion.is_system,
            'created_at': discussion.created_at.isoformat()
        })
    
    return jsonify({'discussions': result}), 200

# 获取指定题目的所有讨论
@app.route('/popquiz/questions/<int:question_id>/discussions', methods=['GET'])
def get_question_discussions(question_id):
    """获取指定题目ID的所有讨论列表"""
    token = request.args.get('token', '').strip()
    if not token:
        return jsonify({'message': '参数错误'}), 400
    
    # 校验token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    
    user_id = session.user_id
    
    # 查找题目
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'message': '题目不存在'}), 404
    
    # 检查用户是否为该题目所属房间的成员
    member = SpeechRoomMember.query.filter_by(room_id=question.room_id, user_id=user_id).first()
    if not member:
        return jsonify({'message': '您不是该题目所属房间的成员'}), 403
    
    # 获取该题目的所有讨论（仅限该房间内）
    discussions = Discussion.query.filter_by(
        question_id=question_id,
        room_id=question.room_id  # 只获取该房间内的讨论
    ).order_by(Discussion.created_at.desc()).all()
    
    result = []
    for discussion in discussions:
        # 获取房间信息
        room = SpeechRoom.query.get(discussion.room_id)
        if not room:
            continue
        
        # 获取用户信息
        user = User.query.get(discussion.user_id)
        username = user.username if user else '未知用户'
        
        result.append({
            'id': discussion.id,
            'room_id': discussion.room_id,
            'room_name': room.name,
            'user_id': discussion.user_id,
            'username': username,
            'content': discussion.content,
            'is_system': discussion.is_system,
            'created_at': discussion.created_at.isoformat()
        })
    
    return jsonify({
        'question_id': question_id,
        'question_content': question.question,
        'discussions': result
    }), 200

# 获取房间内所有已创建的题目
@app.route('/popquiz/speech-rooms/<int:room_id>/questions', methods=['GET'])
def get_room_questions(room_id):
    """获取指定演讲室内所有已创建完成(created=True)的题目列表"""
    token = request.args.get('token', '').strip()
    if not token:
        return jsonify({'message': '参数错误'}), 400
    
    # 校验token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    
    user_id = session.user_id
    
    # 查找房间
    room = SpeechRoom.query.get(room_id)
    if not room:
        return jsonify({'message': '演讲室不存在'}), 404
    
    # 检查用户是否为该演讲室的成员
    member = SpeechRoomMember.query.filter_by(room_id=room_id, user_id=user_id).first()
    if not member:
        return jsonify({'message': '您不是该演讲室的成员'}), 403
    
    # 检查用户权限：只有演讲人和组织者才能查看题目列表
    if room.creator_id != user_id and room.speaker_id != user_id:
        return jsonify({'message': '只有房间创建者和演讲者才能查看题目列表'}), 403
    
    # 获取房间内所有已创建的题目
    # 直接从questions表查询，因为question表中包含room_id
    questions_data = Question.query.filter_by(room_id=room_id, created=1).all()
    
    questions = []
    for question in questions_data:
        questions.append({
            'id': question.id,
            'raw_text': question.raw_text,
            'prompt': question.prompt,
            'question': question.question,
            'option_a': question.option_a,
            'option_b': question.option_b,
            'option_c': question.option_c,
            'option_d': question.option_d,
            'answer': question.answer,
            'created': question.created,
            'published': question.published,
            'created_at': question.created_at.isoformat() if question.created_at else None
        })
    
    return jsonify({
        'room_id': room_id,
        'questions': questions
    }), 200

# 获取房间最新发布还未结束的题目（演讲者和组织者）
@app.route('/popquiz/speech-rooms/<int:room_id>/current-question-for-speaker-and-organizer', methods=['GET'])
def get_current_question_for_speaker_and_organizer(room_id):
    """获取指定演讲室内最新被发布且状态为进行中(0)的题目"""
    token = request.args.get('token', '').strip()
    if not token:
        return jsonify({'message': '参数错误'}), 400
    
    # 校验token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    
    user_id = session.user_id
    
    # 查找房间
    room = SpeechRoom.query.get(room_id)
    if not room:
        return jsonify({'message': '演讲室不存在'}), 404
    
    # 检查用户是否为该演讲室的成员
    member = SpeechRoomMember.query.filter_by(room_id=room_id, user_id=user_id).first()
    if not member:
        return jsonify({'message': '您不是该演讲室的成员'}), 403
    
    # 检查用户权限：只有演讲人和组织者才能查看当前题目
    if room.creator_id != user_id and room.speaker_id != user_id:
        return jsonify({'message': '只有房间创建者和演讲者才能查看当前题目'}), 403
    
    # 获取房间内最新发布且状态为进行中的题目
    published_question = PublishedQuestion.query.filter_by(
        room_id=room_id, 
        status=0  # 0-进行中
    ).order_by(PublishedQuestion.created_at.desc()).first()
    
    if not published_question:
        return jsonify({
            'room_id': room_id,
            'published_question': None,
            'message': '当前没有进行中的题目'
        }), 204
    
    # 获取原题目信息
    question = Question.query.get(published_question.question_id)
    if not question:
        return jsonify({'message': '题目信息不存在'}), 404
    
    return jsonify({
        'room_id': room_id,
        'published_question': {
            'id': published_question.id,
            'question_id': published_question.question_id,
            'start_time': published_question.start_time.isoformat(),
            'end_time': published_question.end_time.isoformat() if published_question.end_time else None,
            'time_limit': published_question.time_limit,
            'status': published_question.status,
            'created_at': published_question.created_at.isoformat(),
            'question': {
                'id': question.id,
                'question': question.question,
                'option_a': question.option_a,
                'option_b': question.option_b,
                'option_c': question.option_c,
                'option_d': question.option_d,
                'answer': question.answer
            }
        }
    }), 200

# 获取房间最新发布还未结束的题目（听众）
@app.route('/popquiz/speech-rooms/<int:room_id>/current-question-for-audience', methods=['GET'])
def get_current_question_for_audience(room_id):
    """获取指定演讲室内最新被发布且状态为进行中(0)的题目，不包含答案"""
    token = request.args.get('token', '').strip()
    if not token:
        return jsonify({'message': '参数错误'}), 400
    
    # 校验token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    
    user_id = session.user_id
    
    # 查找房间
    room = SpeechRoom.query.get(room_id)
    if not room:
        return jsonify({'message': '演讲室不存在'}), 404
    
    # 检查用户是否为该演讲室的成员
    member = SpeechRoomMember.query.filter_by(room_id=room_id, user_id=user_id).first()
    if not member:
        return jsonify({'message': '您不是该演讲室的成员'}), 403
    
    # 获取房间内最新发布且状态为进行中的题目
    published_question = PublishedQuestion.query.filter_by(
        room_id=room_id, 
        status=0  # 0-进行中
    ).order_by(PublishedQuestion.created_at.desc()).first()
    
    if not published_question:
        return jsonify({
            'room_id': room_id,
            'published_question': None,
            'message': '当前没有进行中的题目'
        }), 204
    
    # 获取原题目信息
    question = Question.query.get(published_question.question_id)
    if not question:
        return jsonify({'message': '题目信息不存在'}), 404
    
    # 检查用户是否已答题
    user_answer = QuestionAnswer.query.filter_by(
        room_id=room_id,
        question_id=published_question.question_id,
        user_id=user_id
    ).first()
    
    has_answered = user_answer is not None
    user_answer_choice = user_answer.selected_answer if user_answer else None
    
    return jsonify({
        'room_id': room_id,
        'published_question': {
            'id': published_question.id,
            'question_id': published_question.question_id,
            'start_time': published_question.start_time.isoformat(),
            'end_time': published_question.end_time.isoformat() if published_question.end_time else None,
            'time_limit': published_question.time_limit,
            'status': published_question.status,
            'created_at': published_question.created_at.isoformat(),
            'question': {
                'id': question.id,
                'question': question.question,
                'option_a': question.option_a,
                'option_b': question.option_b,
                'option_c': question.option_c,
                'option_d': question.option_d
                # 不返回答案
            },
            'has_answered': has_answered,
            'user_answer': user_answer_choice
        }
    }), 200

# 发布题目
@app.route('/popquiz/speech-rooms/<int:room_id>/publish-question', methods=['POST'])
def publish_question(room_id):
    """在指定演讲室发布一个题目，开始答题环节"""
    data = request.get_json()
    token = data.get('token', '').strip()
    question_id = data.get('question_id')
    time_limit = data.get('time_limit', 60)  # 默认60秒
    
    if not token or question_id is None:
        return jsonify({'message': '参数错误'}), 400
    
    # 校验token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    
    user_id = session.user_id
    
    # 查找房间
    room = SpeechRoom.query.get(room_id)
    if not room:
        return jsonify({'message': '演讲室不存在'}), 404
    
    # 检查用户是否为该演讲室的成员
    member = SpeechRoomMember.query.filter_by(room_id=room_id, user_id=user_id).first()
    if not member:
        return jsonify({'message': '您不是该演讲室的成员'}), 403
    
    # 检查权限：只有房间创建者和演讲者才能发布题目
    if room.creator_id != user_id and room.speaker_id != user_id:
        return jsonify({'message': '只有房间创建者和演讲者才能发布题目'}), 403
    
    # 检查房间状态：只有进行中(1)的房间才能发布题目
    if room.status != 1:
        return jsonify({'message': '房间状态不允许发布题目'}), 400
    
    # 检查题目是否存在且属于该房间
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'message': '题目不存在'}), 404
    
    # 检查题目是否属于该房间
    if question.room_id != room_id:
        return jsonify({'message': '该题目不属于此演讲室'}), 400
    
    # 检查题目是否已创建完成
    if not question.created:
        return jsonify({'message': '题目尚未创建完成'}), 400
    
    # 检查该房间是否已有进行中的题目
    from datetime import datetime, timedelta
    current_time = datetime.now()
    
    # 检查是否有进行中的题目
    existing_published = PublishedQuestion.query.filter_by(room_id=room_id, status=0).first()
    if existing_published:
        return jsonify({'message': '该房间已有进行中的题目，请等待当前题目结束'}), 409
    
    # 计算结束时间
    end_time = current_time + timedelta(seconds=time_limit)
    
    # 创建发布题目记录
    published_question = PublishedQuestion(
        question_id=question_id,
        room_id=room_id,
        start_time=current_time,
        end_time=end_time,
        time_limit=time_limit,
        status=0  # 0-进行中
    )
    
    # 更新题目的published状态
    question.published = True
    
    db.session.add(published_question)
    db.session.commit()
    
    return jsonify({
        'id': published_question.id,
        'room_id': room_id,
        'question_id': question_id,
        'start_time': published_question.start_time.isoformat(),
        'end_time': published_question.end_time.isoformat(),
        'time_limit': time_limit,
        'status': 0,  # 0-进行中
        'created_at': published_question.created_at.isoformat(),
        'question': {
            'id': question.id,
            'question': question.question,
            'option_a': question.option_a,
            'option_b': question.option_b,
            'option_c': question.option_c,
            'option_d': question.option_d
        },
        'message': '题目发布成功'
    }), 201

# 听众答题
@app.route('/popquiz/speech-rooms/<int:room_id>/answer-question', methods=['POST'])
def answer_question(room_id):
    """听众回答当前进行中的题目"""
    data = request.get_json()
    token = data.get('token', '').strip()
    question_id = data.get('question_id')
    answer = data.get('answer', '').strip()
    
    if not token or question_id is None or not answer:
        return jsonify({'message': '参数错误'}), 400
    
    # 校验答案格式
    if answer not in ['A', 'B', 'C', 'D']:
        return jsonify({'message': '答案格式错误，必须是A、B、C、D之一'}), 400
    
    # 校验token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    
    user_id = session.user_id
    
    # 查找房间
    room = SpeechRoom.query.get(room_id)
    if not room:
        return jsonify({'message': '演讲室不存在'}), 404
    
    # 检查用户是否为该演讲室的成员
    member = SpeechRoomMember.query.filter_by(room_id=room_id, user_id=user_id).first()
    if not member:
        return jsonify({'message': '您不是该演讲室的成员'}), 403
    
    # 检查用户权限：只有听众才能答题（创建者和演讲者不能答题）
    if room.creator_id == user_id or room.speaker_id == user_id:
        return jsonify({'message': '您不是该演讲室的成员或没有答题权限'}), 403
    
    # 检查题目是否存在
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'message': '题目不存在'}), 404
    
    # 检查题目是否属于该房间
    if question.room_id != room_id:
        return jsonify({'message': '该题目不属于此演讲室'}), 404
    
    # 检查是否有进行中的发布题目
    published_question = PublishedQuestion.query.filter_by(
        room_id=room_id,
        question_id=question_id,
        status=0  # 0-进行中
    ).first()
    
    if not published_question:
        return jsonify({'message': '该题目未发布或已结束'}), 409
    
    # 检查题目是否已结束（基于时间）
    from datetime import datetime
    current_time = datetime.now()
    if published_question.end_time and current_time > published_question.end_time:
        return jsonify({'message': '题目已结束，无法答题'}), 409
    
    # 检查用户是否已经回答过这道题目
    existing_answer = QuestionAnswer.query.filter_by(
        room_id=room_id,
        question_id=question_id,
        user_id=user_id
    ).first()
    
    if existing_answer:
        return jsonify({'message': '您已经回答过这道题目'}), 400
    
    # 创建答题记录
    answer_record = QuestionAnswer(
        room_id=room_id,
        question_id=question_id,
        user_id=user_id,
        selected_answer=answer
    )
    
    db.session.add(answer_record)
    db.session.commit()
    
    return jsonify({
        'id': answer_record.id,
        'room_id': room_id,
        'question_id': question_id,
        'user_id': user_id,
        'selected_answer': answer,
        'created_at': answer_record.created_at.isoformat(),
        'message': '答题成功'
    }), 200

# 获取题目答题情况统计（演讲者和组织者）
@app.route('/popquiz/published-questions/<int:published_question_id>/statistics-for-speaker-and-organizer', methods=['GET'])
def get_question_statistics_for_speaker_and_organizer(published_question_id):
    """获取指定发布题目的答题情况统计，包括各选项选择人数和未参与人数"""
    token = request.args.get('token', '').strip()
    if not token:
        return jsonify({'message': '参数错误'}), 400
    
    # 校验token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    
    user_id = session.user_id
    
    # 查找发布题目
    published_question = PublishedQuestion.query.get(published_question_id)
    if not published_question:
        return jsonify({'message': '发布题目不存在'}), 404
    
    room_id = published_question.room_id
    
    # 查找房间
    room = SpeechRoom.query.get(room_id)
    if not room:
        return jsonify({'message': '演讲室不存在'}), 404
    
    # 检查用户是否为该演讲室的成员
    member = SpeechRoomMember.query.filter_by(room_id=room_id, user_id=user_id).first()
    if not member:
        return jsonify({'message': '您不是该演讲室的成员'}), 403
    
    # 检查用户权限：只有演讲人和组织者才能查看统计
    if room.creator_id != user_id and room.speaker_id != user_id:
        return jsonify({'message': '只有房间创建者和演讲者才能查看统计'}), 403
    
    # 获取原题目信息
    question = Question.query.get(published_question.question_id)
    if not question:
        return jsonify({'message': '题目信息不存在'}), 404
    
    # 统计演讲室总参与人数
    total_participants = SpeechRoomMember.query.filter_by(room_id=room_id).count()
    
    # 统计已答题人数
    answered_count = QuestionAnswer.query.filter_by(
        room_id=room_id,
        question_id=published_question.question_id
    ).count()
    
    # 统计未答题人数
    unanswered_count = total_participants - answered_count
    
    # 统计各选项选择人数
    option_a_count = QuestionAnswer.query.filter_by(
        room_id=room_id,
        question_id=published_question.question_id,
        selected_answer='A'
    ).count()
    
    option_b_count = QuestionAnswer.query.filter_by(
        room_id=room_id,
        question_id=published_question.question_id,
        selected_answer='B'
    ).count()
    
    option_c_count = QuestionAnswer.query.filter_by(
        room_id=room_id,
        question_id=published_question.question_id,
        selected_answer='C'
    ).count()
    
    option_d_count = QuestionAnswer.query.filter_by(
        room_id=room_id,
        question_id=published_question.question_id,
        selected_answer='D'
    ).count()
    
    # 统计答对和答错人数
    correct_count = QuestionAnswer.query.filter_by(
        room_id=room_id,
        question_id=published_question.question_id,
        selected_answer=question.answer
    ).count()
    
    wrong_count = answered_count - correct_count
    
    # 计算正确率
    accuracy_rate = round((correct_count / answered_count * 100), 2) if answered_count > 0 else 0.0
    
    return jsonify({
        'published_question_id': published_question_id,
        'room_id': room_id,
        'question_info': {
            'id': question.id,
            'question': question.question,
            'option_a': question.option_a,
            'option_b': question.option_b,
            'option_c': question.option_c,
            'option_d': question.option_d,
            'answer': question.answer
        },
        'statistics': {
            'total_participants': total_participants,
            'answered_count': answered_count,
            'unanswered_count': unanswered_count,
            'option_a_count': option_a_count,
            'option_b_count': option_b_count,
            'option_c_count': option_c_count,
            'option_d_count': option_d_count,
            'correct_count': correct_count,
            'wrong_count': wrong_count,
            'accuracy_rate': accuracy_rate
        },
        'time_info': {
            'start_time': published_question.start_time.isoformat(),
            'end_time': published_question.end_time.isoformat() if published_question.end_time else None,
            'time_limit': published_question.time_limit,
            'status': published_question.status
        }
    }), 200

# 获取题目答题情况统计（听众）
@app.route('/popquiz/published-questions/<int:published_question_id>/statistics-for-audience', methods=['GET'])
def get_question_statistics_for_audience(published_question_id):
    """听众获取指定发布题目的答题情况统计，只有在题目结束时才返回正确答案和正确率"""
    token = request.args.get('token', '').strip()
    if not token:
        return jsonify({'message': '参数错误'}), 400
    
    # 校验token
    session = UserSession.query.filter_by(session_token=token, is_expired=False).first()
    if not session:
        return jsonify({'message': 'token无效或已过期'}), 401
    
    user_id = session.user_id
    
    # 查找发布题目
    published_question = PublishedQuestion.query.get(published_question_id)
    if not published_question:
        return jsonify({'message': '发布题目不存在'}), 404
    
    room_id = published_question.room_id
    
    # 查找房间
    room = SpeechRoom.query.get(room_id)
    if not room:
        return jsonify({'message': '演讲室不存在'}), 404
    
    # 检查用户是否为该演讲室的成员
    member = SpeechRoomMember.query.filter_by(room_id=room_id, user_id=user_id).first()
    if not member:
        return jsonify({'message': '您不是该演讲室的成员'}), 403
    
    # 获取原题目信息
    question = Question.query.get(published_question.question_id)
    if not question:
        return jsonify({'message': '题目信息不存在'}), 404
    
    # 统计演讲室总参与人数
    total_participants = SpeechRoomMember.query.filter_by(room_id=room_id).count()
    
    # 统计已答题人数
    answered_count = QuestionAnswer.query.filter_by(
        room_id=room_id,
        question_id=published_question.question_id
    ).count()
    
    # 统计未答题人数
    unanswered_count = total_participants - answered_count
    
    # 统计各选项选择人数
    option_a_count = QuestionAnswer.query.filter_by(
        room_id=room_id,
        question_id=published_question.question_id,
        selected_answer='A'
    ).count()
    
    option_b_count = QuestionAnswer.query.filter_by(
        room_id=room_id,
        question_id=published_question.question_id,
        selected_answer='B'
    ).count()
    
    option_c_count = QuestionAnswer.query.filter_by(
        room_id=room_id,
        question_id=published_question.question_id,
        selected_answer='C'
    ).count()
    
    option_d_count = QuestionAnswer.query.filter_by(
        room_id=room_id,
        question_id=published_question.question_id,
        selected_answer='D'
    ).count()
    
    # 检查题目是否已结束
    from datetime import datetime
    is_ended = published_question.status == 1 or (published_question.end_time and datetime.now() > published_question.end_time)
    
    # 只有在题目结束时才返回正确答案和正确率
    if is_ended:
        correct_count = QuestionAnswer.query.filter_by(
            room_id=room_id,
            question_id=published_question.question_id,
            selected_answer=question.answer
        ).count()
        
        wrong_count = answered_count - correct_count
        accuracy_rate = round((correct_count / answered_count * 100), 2) if answered_count > 0 else 0.0
        
        question_answer = question.answer
    else:
        correct_count = None
        wrong_count = None
        accuracy_rate = None
        question_answer = None
    
    return jsonify({
        'published_question_id': published_question_id,
        'room_id': room_id,
        'question_info': {
            'id': question.id,
            'question': question.question,
            'option_a': question.option_a,
            'option_b': question.option_b,
            'option_c': question.option_c,
            'option_d': question.option_d,
            'answer': question_answer  # 只有在题目结束时才返回
        },
        'statistics': {
            'total_participants': total_participants,
            'answered_count': answered_count,
            'unanswered_count': unanswered_count,
            'option_a_count': option_a_count,
            'option_b_count': option_b_count,
            'option_c_count': option_c_count,
            'option_d_count': option_d_count,
            'correct_count': correct_count,  # 只有在题目结束时才返回
            'wrong_count': wrong_count,  # 只有在题目结束时才返回
            'accuracy_rate': accuracy_rate  # 只有在题目结束时才返回
        },
        'time_info': {
            'start_time': published_question.start_time.isoformat(),
            'end_time': published_question.end_time.isoformat() if published_question.end_time else None,
            'time_limit': published_question.time_limit,
            'status': published_question.status
        }
    }), 200

@app.route('/popquiz/users', methods=['GET'])
def get_all_users():
    """获取所有用户列表，供管理后台使用"""
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'username': user.username,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        })
    return jsonify({'users': result}), 200

@app.route('/popquiz/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除指定ID的用户，管理后台用"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': '删除成功', 'id': user_id}), 200

# 新增用户接口（cjy修改）
@app.route('/popquiz/users', methods=['POST'])
def add_user():
    """
    管理后台新增用户（cjy修改）
    请求参数：username, password
    """
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'message': '参数错误'}), 400
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 400
    # 创建新用户
    from werkzeug.security import generate_password_hash
    user = User(username=username, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'message': '新增成功'}), 201

# 编辑用户接口（cjy修改）
@app.route('/popquiz/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    """
    管理后台编辑用户（cjy修改）
    请求参数：username(可选), password(可选)
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    # 检查用户名是否已存在（如果有修改）
    if username and username != user.username:
        if User.query.filter_by(username=username).first():
            return jsonify({'message': '用户名已存在'}), 400
        user.username = username
    if password:
        from werkzeug.security import generate_password_hash
        user.password = generate_password_hash(password)
    db.session.commit()
    return jsonify({'id': user.id, 'message': '编辑成功'}), 200

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True,allow_unsafe_werkzeug=True)
