#!/usr/bin/env python3
"""
Test the complete document analysis flow
"""

import os
from src.llm import chat

# Test document text
test_document = """
John Doe
Software Engineer
Email: john.doe@email.com
Phone: (555) 123-4567

EXPERIENCE:
Software Engineer at TechCorp (2020-2024)
- Developed web applications using Python and JavaScript
- Led a team of 5 developers on multiple projects
- Improved application performance by 30%
- Mentored junior developers

SKILLS:
- Python, JavaScript, React, Node.js
- AWS, Docker, Kubernetes
- Agile methodologies, Scrum
- Team leadership and project management

EDUCATION:
Bachelor of Science in Computer Science
University of Technology (2016-2020)
"""

# Test the analysis
print("🧪 Testing document analysis...")
print(f"Document length: {len(test_document)} characters")

# Create the prompt
prompt = f"""
Document: {test_document}

Question: Analyze this candidate for a senior software engineering position

Provide a concise, professional answer based on the document. Focus on key insights for leadership.
"""

print("📝 Sending to LLM...")
response = chat([{"role": "user", "content": prompt}])

print("✅ Response received:")
print("=" * 50)
print(response)
print("=" * 50)
