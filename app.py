# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000"])

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    email = db.Column(db.String(120), primary_key=True)
    phone = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(120))  # New field

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(120), nullable=False)
    recipient = db.Column(db.String(120), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    delivered = db.Column(db.Boolean, default=False)

sockets = {} 



@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    phone = data.get('phone')
    name = data.get('name') or email.split('@')[0]  # Use part before @ if no name provided

    if not email or not phone:
        return jsonify({"success": False, "message": "Email and phone required."}), 400

    if User.query.get(email):
        return jsonify({"success": False, "message": "Email already registered."})

    new_user = User(email=email, phone=phone, name=name)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"success": True})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    user = User.query.get(email)
    if user:
        return jsonify({"success": True, "phone": user.phone})
    return jsonify({"success": False, "message": "User not found."})

@app.route('/search', methods=['GET'])
def search():
    key = request.args.get('key')
    user = User.query.filter((User.email == key) | (User.phone == key)).first()
    if user:
        online = sockets.get(user.email, {}).get('online', False)
        return jsonify({
            "found": True,
            "email": user.email,
            "phone": user.phone,
            "name": user.name,
            "online": online
        })
    return jsonify({"found": False})

@app.route('/messages/<email>', methods=['GET'])
def get_messages(email):
    msgs = Message.query.filter(
        (Message.sender == email) | (Message.recipient == email)
    ).order_by(Message.timestamp).all()
    return jsonify([{
        "from": m.sender,
        "to": m.recipient,
        "text": m.text,
        "timestamp": m.timestamp.isoformat()
    } for m in msgs])

@socketio.on('connect')
def handle_connect():
    print(f"[Socket] Client connected: {request.sid}")

@socketio.on('register')
def handle_register(data):
    email = data.get('email')
    if not email:
        return

    sockets[email] = {'sid': request.sid, 'online': True}
    print(f"[Socket] {email} registered with sid {request.sid}")

    emit('status_update', {'email': email, 'online': True}, broadcast=True)

    # Send undelivered messages
    undelivered = Message.query.filter_by(recipient=email, delivered=False).all()
    for msg in undelivered:
        emit('message', {
            'from': msg.sender,
            'text': msg.text,
            'timestamp': msg.timestamp.isoformat()
        }, to=request.sid)
        msg.delivered = True
    db.session.commit()

@socketio.on('send_message')
def handle_message(data):
    sender = data.get('from')
    recipient = data.get('to')
    text = data.get('text')

    if not sender or not recipient or not text:
        return

    msg = Message(sender=sender, recipient=recipient, text=text, timestamp=datetime.utcnow())
    db.session.add(msg)

    recipient_info = sockets.get(recipient)
    if recipient_info and recipient_info['online']:
        emit('message', {
            'from': sender,
            'to': recipient,
            'text': text,
            'timestamp': msg.timestamp.isoformat()
        }, to=recipient_info['sid'])
        msg.delivered = True

    sender_info = sockets.get(sender)
    if sender_info and sender_info['online']:
        emit('message', {
            'from': sender,
            'to': recipient,
            'text': text,
            'timestamp': msg.timestamp.isoformat()
        }, to=sender_info['sid'])

    db.session.commit()

    print(f"[Message] {sender} -> {recipient}: {text}")

@socketio.on('typing')
def handle_typing(data):
    sender = data.get('from')
    recipient = data.get('to')

    if not sender or not recipient:
        return

    recipient_info = sockets.get(recipient)
    if recipient_info and recipient_info['online']:
        emit('typing', {'from': sender, 'to': recipient}, to=recipient_info['sid'])

@socketio.on('disconnect')
def handle_disconnect():
    for email, info in list(sockets.items()):
        if info['sid'] == request.sid:
            sockets[email]['online'] = False
            print(f"[Socket] {email} disconnected")
            
            # Notify other users about the status change
            emit('status_update', {'email': email, 'online': False}, broadcast=True)
            break

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000)
