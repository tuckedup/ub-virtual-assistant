from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from chatbot import UBChatbot
import os
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Rate limiting to prevent abuse
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize chatbot
chatbot = UBChatbot()

# Store conversation history
conversations = {}

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
@limiter.limit("30 per minute")
def chat():
    """Handle chat messages"""
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', '')
    
    if not session_id:
        session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()
    
    # Check if user is authenticated
    authenticated = session.get('authenticated', False)
    
    # Get response from chatbot
    bot_response = chatbot.generate_response(user_message, authenticated)
    
    # Store conversation
    if session_id not in conversations:
        conversations[session_id] = []
    
    conversations[session_id].append({
        'timestamp': datetime.now().isoformat(),
        'user': user_message,
        'bot': bot_response
    })
    
    # Keep only last 50 messages per session
    if len(conversations[session_id]) > 50:
        conversations[session_id] = conversations[session_id][-50:]
    
    return jsonify({
        'response': bot_response,
        'session_id': session_id,
        'authenticated': authenticated
    })

@app.route('/authenticate', methods=['POST'])
def authenticate():
    """Handle authentication requests"""
    data = request.json
    student_id = data.get('student_id', '')
    password = data.get('password', '')
    
    # IMPORTANT: This is a mock authentication
    # In production, integrate with UB's actual authentication system (Shibboleth/LDAP)
    
    # For demo purposes only - DO NOT USE IN PRODUCTION
    if len(student_id) >= 7 and password:
        session['authenticated'] = True
        session['student_id'] = student_id
        return jsonify({
            'success': True,
            'message': 'Authentication successful'
        })
    
    return jsonify({
        'success': False,
        'message': 'Invalid credentials'
    }), 401

@app.route('/logout', methods=['POST'])
def logout():
    """Handle logout"""
    session.clear()
    return jsonify({'success': True})

@app.route('/feedback', methods=['POST'])
def feedback():
    """Collect user feedback"""
    data = request.json
    feedback_text = data.get('feedback', '')
    rating = data.get('rating', 0)
    session_id = data.get('session_id', '')
    
    # Store feedback (in production, save to database)
    feedback_data = {
        'timestamp': datetime.now().isoformat(),
        'session_id': session_id,
        'feedback': feedback_text,
        'rating': rating
    }
    
    # Log feedback (replace with database storage)
    with open('feedback.log', 'a') as f:
        f.write(f"{feedback_data}\n")
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)