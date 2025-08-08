#!/usr/bin/env python3
"""
Simple Flask Server for Insurance Query System
"""

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import json
import re

app = Flask(__name__)
CORS(app)

# Simple mock document
MOCK_POLICY = {
    'inclusions': {
        'general_medical': 500000,
        'maternity_care': 200000,
        'cardiac_surgery': 1000000,
        'cancer_treatment': 1500000,
        'emergency_care': 300000
    },
    'exclusions': [
        'IVF treatment',
        'in-vitro fertilization', 
        'fertility treatments',
        'cosmetic surgery',
        'dental implants'
    ]
}

@app.route('/')
def index():
    return """
    <html>
    <head><title>Insurance Query System</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>🎯 Insurance Query System</h1>
        <p><strong>Server is running successfully!</strong></p>
        <hr>
        <h3>Test the system:</h3>
        <form id="queryForm">
            <label>Enter your query:</label><br>
            <input type="text" id="queryInput" placeholder="e.g., IVF treatment" style="width: 300px; padding: 5px;"><br><br>
            <button type="button" onclick="submitQuery()">Submit Query</button>
        </form>
        <div id="result" style="margin-top: 20px; padding: 10px; background: #f0f0f0;"></div>
        
        <h3>API Endpoints:</h3>
        <ul>
            <li><a href="/health">Health Check</a></li>
            <li>POST /query - Submit insurance query</li>
        </ul>
        
        <script>
        async function submitQuery() {
            const query = document.getElementById('queryInput').value;
            if (!query) return;
            
            try {
                const response = await fetch('/query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query})
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = 
                    '<strong>Decision:</strong> ' + result.decision + '<br>' +
                    '<strong>Confidence:</strong> ' + result.confidence + '%<br>' +
                    '<strong>Reason:</strong> ' + result.reason;
            } catch (error) {
                document.getElementById('result').innerHTML = 'Error: ' + error;
            }
        }
        </script>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'server': 'running',
        'message': 'Insurance Query System is operational'
    })

@app.route('/query', methods=['POST'])
def query():
    try:
        data = request.get_json()
        query_text = data.get('query', '').lower()
        
        # Simple decision logic
        decision = 'APPROVED'
        reason = 'General medical coverage'
        confidence = 80
        amount = 500000
        
        # Check exclusions
        for exclusion in MOCK_POLICY['exclusions']:
            if exclusion.lower() in query_text:
                decision = 'REJECTED'
                reason = f'Excluded: {exclusion}'
                confidence = 90
                amount = 0
                break
        
        # Check specific inclusions
        if 'cardiac' in query_text or 'heart' in query_text:
            decision = 'APPROVED'
            reason = 'Cardiac surgery coverage'
            amount = 1000000
            confidence = 95
        elif 'cancer' in query_text:
            decision = 'APPROVED'
            reason = 'Cancer treatment coverage'
            amount = 1500000
            confidence = 95
        
        return jsonify({
            'decision': decision,
            'reason': reason,
            'confidence': confidence,
            'amount': amount,
            'query': query_text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Simple Insurance Query Server...")
    print("🌐 Server will be available at: http://localhost:5000")
    print("✅ Ready to process insurance queries!")
    app.run(debug=True, host='127.0.0.1', port=5000)
