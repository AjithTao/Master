from utils.slot_based_nlu import SlotBasedNLU
from utils.enhanced_jql_training_loader import EnhancedJQLTrainingLoader
import json

def comprehensive_test():
    """Comprehensive test of the slot-based NLU system"""
    print("🚀 COMPREHENSIVE SLOT-BASED NLU SYSTEM TEST")
    print("=" * 60)
    
    # Initialize components
    nlu = SlotBasedNLU()
    loader = EnhancedJQLTrainingLoader('data/jira_ai_training_pack.json')
    
    # Test cases covering all major scenarios
    test_cases = [
        {
            "query": "give me ccm project open stories",
            "expected_slots": ["project", "issuetype", "status_category"],
            "expected_intent": "ccm_project_open_stories"
        },
        {
            "query": "show me ashwin's current sprint work",
            "expected_slots": ["assignee"],
            "expected_intent": None  # Should fall back to advanced JQL
        },
        {
            "query": "high priority bugs in CCM",
            "expected_slots": ["project", "issuetype", "priority"],
            "expected_intent": "project_by_priority"
        },
        {
            "query": "what did ajith finish last week",
            "expected_slots": ["assignee", "date_range"],
            "expected_intent": "assignee_done_last_week"
        },
        {
            "query": "overdue tickets in CCM",
            "expected_slots": ["project"],
            "expected_intent": "overdue"
        },
        {
            "query": "summary contains 'login'",
            "expected_slots": ["text"],
            "expected_intent": "text_search_summary"
        },
        {
            "query": "top 5 oldest open items",
            "expected_slots": ["quantity", "order", "status_category"],
            "expected_intent": "top_oldest_open"
        },
        {
            "query": "unassigned in CCM",
            "expected_slots": ["project"],
            "expected_intent": "no_assignee"
        },
        {
            "query": "done today in CCM",
            "expected_slots": ["project", "date_range"],
            "expected_intent": "moved_to_done_today"
        },
        {
            "query": "epic CCM-100 progress",
            "expected_slots": ["epic"],
            "expected_intent": "epic_progress"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: '{test_case['query']}'")
        
        # Test slot extraction
        slots = nlu.extract_slots(test_case['query'])
        extracted_slots = []
        
        if slots.project:
            extracted_slots.append("project")
        if slots.assignee:
            extracted_slots.append("assignee")
        if slots.issuetype:
            extracted_slots.append("issuetype")
        if slots.status_category:
            extracted_slots.append("status_category")
        if slots.priority:
            extracted_slots.append("priority")
        if slots.text:
            extracted_slots.append("text")
        if slots.quantity:
            extracted_slots.append("quantity")
        if slots.order:
            extracted_slots.append("order")
        if slots.date_range:
            extracted_slots.append("date_range")
        if slots.epic:
            extracted_slots.append("epic")
        
        print(f"   📊 Extracted slots: {extracted_slots}")
        print(f"   🎯 Expected slots: {test_case['expected_slots']}")
        
        # Test template matching
        match = loader.find(test_case['query'])
        if match:
            intent = match.get('intent')
            jql = match.get('jql')
            print(f"   ✅ Intent: {intent}")
            print(f"   🔧 JQL: {jql}")
            
            if 'slots_used' in match:
                print(f"   🎪 Slots Used: {match['slots_used']}")
        else:
            print("   ❌ No template match found")
            intent = None
        
        # Check if test passed
        slot_match = set(extracted_slots) == set(test_case['expected_slots'])
        intent_match = intent == test_case['expected_intent'] if test_case['expected_intent'] else True
        
        if slot_match and intent_match:
            print("   ✅ PASS")
            passed += 1
        else:
            print("   ❌ FAIL")
            if not slot_match:
                print(f"      Slot mismatch: got {extracted_slots}, expected {test_case['expected_slots']}")
            if not intent_match:
                print(f"      Intent mismatch: got {intent}, expected {test_case['expected_intent']}")
    
    print(f"\n📈 RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Slot-based NLU system is working correctly.")
    else:
        print("⚠️  Some tests failed. Review the output above for details.")
    
    return passed == total

def test_context_memory():
    """Test context memory functionality"""
    print("\n🧠 TESTING CONTEXT MEMORY")
    print("=" * 30)
    
    loader = EnhancedJQLTrainingLoader('data/jira_ai_training_pack.json')
    
    # Set context
    loader.set_context(project="CCM")
    print(f"✅ Set project context to: CCM")
    
    # Test context retrieval
    context_project = loader.get_context_project()
    print(f"✅ Retrieved project context: {context_project}")
    
    # Test query with context
    match = loader.find("open stories")
    if match:
        print(f"✅ Context-aware query successful")
        print(f"   JQL: {match.get('jql')}")
        if 'slots_used' in match:
            print(f"   Slots Used: {match['slots_used']}")
    else:
        print("❌ Context-aware query failed")

if __name__ == "__main__":
    success = comprehensive_test()
    test_context_memory()
    
    if success:
        print("\n🎯 SYSTEM STATUS: ✅ READY FOR PRODUCTION")
    else:
        print("\n🎯 SYSTEM STATUS: ⚠️  NEEDS ATTENTION")
