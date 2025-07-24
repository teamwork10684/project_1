# connect事件及其相关事件
1. speakerroom和room挂载时
    * 调用wsManager.connect(roomId,user_id,username,role)函数
    * 通过eventBus.on()方法挂载`userJoined`与`roomUsersUpdated`信号
2. websocket.js创建连接
    * connect()方法建立与websocket_handler.py的连接,同时调用setupEventListeners()方法，连接成功后自动触发`connect`事件。
    * setupEventListeners()方法设置事件监听器，其中包含`connect`事件和其它事件。
    * 监听到`connect`事件，调用joinRoom()函数
    * joinRoom()内部触发`join_room`事件,传出room_id,user_id,username,role
3. websocket_handler.py监听到 `join_room`事件
    * 向room_id号房间发送 `user_joined`事件
    * 向触发这一事件的连接发送`room_users`事件，传递users(人员列表),total_online(在线人员数)
4. websocket.js监听到`user_joined`事件和`room_users`事件
    * 挂载过`userJoined`与`roomUsersUpdated`信号的组件被调用回调函数
5. speakerroom和room中handleUserJoined()方法和handleRoomUsersUpdated()方法被调用



# question_generated事件
建立连接过程已在connect事件及其相关事件中详细描述过，以下默认连接已经建立
1. speakerroom挂载时，通过eventBus.on()方法挂载`questionGenerated`信号
2. app.py生成完题目，通过emit()方法触发`question_generated`事件
3. websocket.js监听到`question_generated`事件，挂载过`questionGenerated`信号的组件被调用回调函数
4. speakerroom中的对应函数被调用