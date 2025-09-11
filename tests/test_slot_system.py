from utils.slot_based_nlu import SlotBasedNLU
from utils.enhanced_jql_training_loader import EnhancedJQLTrainingLoader
import json

def test_slot_extraction():
    """Test slot extraction functionality"""
    print("🔍 Testing Slot Extraction...")
    
    nlu = SlotBasedNLU()
    
    test_queries = [
        "give me ccm project open stories",
        "show me ashwin's current sprint work",
        "high priority bugs in CCM",
        "what did ajith finish last week",
        "overdue tickets in project",
        "summary contains 'login'",
        "top 5 oldest open items"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        slots = nlu.extract_slots(query)
        
        # Print extracted slots
        slot_info = []
        if slots.project:
            slot_info.append(f"Project: {slots.project.value}")
        if slots.assignee:
            slot_info.append(f"Assignee: {slots.assignee.value}")
        if slots.issuetype:
            slot_info.append(f"IssueType: {slots.issuetype.value}")
        if slots.status_category:
            slot_info.append(f"StatusCategory: {slots.status_category.value}")
        if slots.priority:
            slot_info.append(f"Priority: {slots.priority.value}")
        if slots.text:
            slot_info.append(f"Text: {slots.text.value}")
        if slots.quantity:
            slot_info.append(f"Quantity: {slots.quantity.value}")
        if slots.order:
            slot_info.append(f"Order: {slots.order.value}")
        
        if slot_info:
            print(f"   Extracted: {', '.join(slot_info)}")
        else:
            print("   No slots extracted")

def test_template_processing():
    """Test template processing with slot composition"""
    print("\n🔧 Testing Template Processing...")
    
    try:
        loader = EnhancedJQLTrainingLoader('data/jira_ai_training_pack.json')
        print("✅ Enhanced training loader initialized")
        
        test_queries = [
            "give me ccm project open stories",
            "open stories in CCM",
            "high priority in CCM",
            "ashwin stories in CCM"
        ]
        
        for query in test_queries:
            print(f"\n📝 Query: '{query}'")
            match = loader.find(query)
            
            if match:
                print(f"   Intent: {match.get('intent', 'Unknown')}")
                print(f"   JQL: {match.get('jql', 'No JQL')}")
                print(f"   Template: {match.get('template', 'No template')}")
                if 'slots_used' in match:
                    print(f"   Slots Used: {match['slots_used']}")
            else:
                print("   No match found")
                
    except Exception as e:
        print(f"❌ Template processing failed: {e}")

def test_jql_composition():
    """Test JQL composition from templates"""
    print("\n🎯 Testing JQL Composition...")
    
    nlu = SlotBasedNLU()
    
    # Test template
    template = "project = ${PROJECT} AND statusCategory != Done AND issuetype in (${ISSUETYPE}) ORDER BY ${ORDER}"
    
    # Test query
    query = "give me ccm project open stories"
    slots = nlu.extract_slots(query)
    
    print(f"📝 Query: '{query}'")
    print(f"🔧 Template: '{template}'")
    
    composed_jql = nlu.compose_jql(slots, template)
    print(f"✅ Composed JQL: '{composed_jql}'")

if __name__ == "__main__":
    test_slot_extraction()
    test_template_processing()
    test_jql_composition()
