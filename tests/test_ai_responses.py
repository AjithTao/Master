#!/usr/bin/env python3
"""
Test script to check AI responses for 10 different types of questions
"""
import requests
import json
import time

# Test questions covering different scenarios
test_questions = [
    # 1. Specific ticket question
    "Tell me about CCM-283",
    
    # 2. Assignee question
    "What's Ashwin working on?",
    
    # 3. Project question
    "How many projects do we have?",
    
    # 4. Sprint question
    "What's our current sprint?",
    
    # 5. Status question
    "What's in progress?",
    
    # 6. Issue type question
    "How many stories do we have?",
    
    # 7. Analytics question
    "Give me a summary",
    
    # 8. General question
    "Hello, how are you?",
    
    # 9. Help question
    "What can you help me with?",
    
    # 10. Edge case question
    "Show me tickets assigned to John Doe"
]

def test_ai_response(question):
    """Test a single question and return the response"""
    try:
        response = requests.post(
            "http://localhost:8000/api/chat",
            json={"message": question},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response")
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except requests.exceptions.RequestException as e:
        return f"Connection error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    print("🤖 Testing AI Responses with 10 Different Questions\n")
    print("=" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Question {i}: {question}")
        print("-" * 40)
        
        response = test_ai_response(question)
        print(f"🤖 AI Response: {response}")
        
        # Add a small delay between requests
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("✅ Testing completed!")

if __name__ == "__main__":
    main()
