#!/usr/bin/env python3
"""
Test the chatbot with real Jira data to show correct responses
"""

import requests
import json
import time

def test_chatbot():
    base_url = 'http://127.0.0.1:8000'
    
    test_queries = [
        'details on ccm-283',
        'give me the list of projects present', 
        'show me Ashwini stories',
        'what are the highest priority bugs',
        'jquery code to search for issues'
    ]
    
    print('🤖 Testing Chatbot with Real Jira Data')
    print('=' * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f'\n📝 Query {i}: {query}')
        print('-' * 30)
        
        try:
            response = requests.post(f'{base_url}/chat', 
                                   json={'message': query}, 
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', 'No response')
                print(f'✅ Response: {response_text}')
                
                # Show if it's data-driven or generic
                if len(response_text) > 200 and ('CCM-283' in response_text or 'project' in response_text.lower()):
                    print('🎯 Data-driven response detected!')
                elif 'I don\'t have access' in response_text or 'If you can provide' in response_text:
                    print('⚠️ Generic fallback response')
                    
            else:
                print(f'❌ Error {response.status_code}: {response.text}')
                
        except Exception as e:
            print(f'❌ Exception: {str(e)}')
        
        print()
        time.sleep(1)  # Brief pause between requests

if __name__ == '__main__':
    test_chatbot()
