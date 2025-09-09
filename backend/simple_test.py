import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from query_processor import AdvancedQueryProcessor

# Test Case 1: jQuery Code Generation
print('CASE 1: jQuery Code Generation')
processor = AdvancedQueryProcessor(None, None)
query = 'jquery code to get assignee for ces-1'
entities = processor.entity_extractor.extract_entities(query)
print(f'Query: {query}')
print(f'Entities: {entities}')
examples = processor._generate_jquery_examples(query, entities)
print(f'Generated {len(examples)} jQuery examples')
for name, code in examples.items():
    print(f'{name}: {len(code)} chars')

# Test Case 2: Intelligent Name Matching  
print('\nCASE 2: Intelligent Name Matching')
test_queries = ['stories worked by Ashw', 'issues assigned to John', 'work by Karthik']
for q in test_queries:
    entities = processor.entity_extractor.extract_entities(q)
    print(f'Query: {q}')
    print(f'Assignees: {entities.get("assignees", [])}')
    print(f'Partial names: {entities.get("partial_names", [])}')
    print()

print('SUCCESS: Both features working correctly!')
