#  conekt

a simple p2p chat app that lets u talk to ppl .

## what we got here

- **super simple login/signup**: just email n phone, ez pz
- **real-time messaging**: no need to refresh like its 2005
- **see who's online**: green dot when they're here, last seen when they're not
- **typing indicators**: see when someone's typing (and deleting and typing again lol)
- **chat history**: msgs dont disappear when u close the app
- **clean ui**: looks good but we didn't try too hard

## how we built it

we kept it simple:

### frontend (React)
- React for the ui stuff
- Socket.io-client for real-time things
- Axios for talking to backend
- CSS-in-JS cuz why not

### backend (Python)
- Flask for the basic server stuff
- Flask-SocketIO for websocket magic
- SQLAlchemy + SQLite to save everything
- Simple in-memory user tracking

## features that actually work

-  Make an account with email/phone
-  Search for other users
-  Send/receive messages instantly
-  See who's online/offline
-  Works on mobile too

## how to run this thing

1. clone it
2. install stuff:
```bash
# backend
cd p2p_chat
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install flask flask-socketio flask-cors flask-sqlalchemy

# frontend
cd p2p-chat-frontend
npm install
```

3. start it:
```bash
# terminal 1 - backend
python app.py

# terminal 2 - frontend
npm start
```

4. go to `http://localhost:3000` and chat away

## known issues (we'll fix these... maybe)

- no message delete (just dont send embarassing msgs)
- probably more but we're pretending they dont exist

## want to help?

sure why not! just:
1. fork it
2. do ur thing
3. make a PR
4. we'll look at it when we remember

made with 💖 and ☕️ by someone who should probably be sleeping
# p2pchat
