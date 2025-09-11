import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from ai_engine import AdvancedAIEngine

ai = AdvancedAIEngine()
query = 'jquery code to get assignee for ces-1'
intent = ai.analyze_query_intent(query)
print('AI Intent Analysis:', intent)

prompt = ai._build_context_prompt(query, intent, {})
print('Context prompt contains jQuery instructions:', 'jquery' in prompt.lower())
print('Context prompt contains name matching:', 'name' in prompt.lower() and 'matching' in prompt.lower())
print('Prompt length:', len(prompt))

# Test another query
query2 = 'stories worked by Ashw'
intent2 = ai.analyze_query_intent(query2)
print('\nQuery 2:', query2)
print('Intent 2:', intent2)
prompt2 = ai._build_context_prompt(query2, intent2, {})
print('Contains name matching instructions:', 'name' in prompt2.lower() and 'matching' in prompt2.lower())
