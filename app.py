from flask import Flask, request, jsonify
from datetime import datetime, timezone
import json
import os

app = Flask(__name__)

# Store recent webhooks in memory (last 100)
recent_webhooks = []

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'webhooks_received': len(recent_webhooks)
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    # Log it
    webhook_entry = {
        'received_at': datetime.now(timezone.utc).isoformat(),
        'data': data
    }
    recent_webhooks.append(webhook_entry)
    
    # Keep only last 100
    if len(recent_webhooks) > 100:
        recent_webhooks.pop(0)
    
    # Print for logs
    print(f"\n{'='*50}")
    print(f"WEBHOOK RECEIVED: {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*50}")
    
    # Extract key info if it's a transaction
    if isinstance(data, list) and len(data) > 0:
        for tx in data:
            tx_type = tx.get('type', 'UNKNOWN')
            source = tx.get('source', 'UNKNOWN')
            print(f"Type: {tx_type}, Source: {source}")
            
            # Token transfers
            if 'tokenTransfers' in tx:
                for transfer in tx.get('tokenTransfers', []):
                    print(f"  Token: {transfer.get('mint', 'N/A')[:20]}...")
                    print(f"  From: {transfer.get('fromUserAccount', 'N/A')[:20]}...")
                    print(f"  To: {transfer.get('toUserAccount', 'N/A')[:20]}...")
    
    return jsonify({'status': 'received'}), 200

@app.route('/recent', methods=['GET'])
def get_recent():
    return jsonify(recent_webhooks[-10:])

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'service': 'Wallet Hunter Webhook Receiver',
        'endpoints': {
            '/health': 'Health check',
            '/webhook': 'POST - Helius webhook receiver',
            '/recent': 'GET - View last 10 webhooks'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
