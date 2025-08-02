from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
from services.negotiation_service import NegotiationService
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global negotiation service
negotiation_service = NegotiationService()

@app.route('/')
def index():
    """Main negotiation interface"""
    return render_template('negotiation.html')

@app.route('/api/start_negotiation', methods=['POST'])
def start_negotiation():
    """Start a new negotiation session"""
    try:
        data = request.json
        
        result = negotiation_service.start_negotiation(
            item=data['item'],
            item_details=data['item_details'],
            seller_cost=float(data['seller_cost']),
            seller_target=float(data['seller_target']),
            seller_min=float(data['seller_min']),
            buyer_target=float(data['buyer_target']),
            buyer_max=float(data['buyer_max'])
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/buyer_respond', methods=['POST'])
def buyer_respond():
    """Process buyer response"""
    try:
        data = request.json
        result = negotiation_service.process_buyer_response(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/seller_respond', methods=['POST'])
def seller_respond():
    """Process seller response"""
    try:
        data = request.json
        result = negotiation_service.process_seller_response(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/auto_negotiate', methods=['POST'])
def auto_negotiate():
    """Run automatic negotiation"""
    try:
        data = request.json
        rounds = data.get('rounds', 5)
        results = negotiation_service.auto_negotiate(rounds)
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/negotiation_status', methods=['GET'])
def negotiation_status():
    """Get current negotiation status"""
    try:
        summary = negotiation_service.get_negotiation_summary()
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# WebSocket events for real-time communication
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'message': 'Connected to AI Negotiation System'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('start_negotiation')
def handle_start_negotiation(data):
    """Handle negotiation start via WebSocket"""
    result = negotiation_service.start_negotiation(
        item=data['item'],
        item_details=data['item_details'],
        seller_cost=float(data['seller_cost']),
        seller_target=float(data['seller_target']),
        seller_min=float(data['seller_min']),
        buyer_target=float(data['buyer_target']),
        buyer_max=float(data['buyer_max'])
    )
    emit('negotiation_update', result)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
