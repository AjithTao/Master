from typing import Any, Dict
from jira_client import JiraClient
from entity_extractor import extract_entities, fill_defaults
from ai_summarizer import summarize


async def handle_user_query(user_query: str, jira_client: JiraClient) -> Dict[str, str]:
    intent = jira_client.match_intent(user_query)
    if not intent:
        return {"text": "I couldn’t map that request to a known intent. Try rephrasing (e.g., 'open bugs in DOCS')."}

    entities = extract_entities(user_query, jira_client=jira_client)
    entities = fill_defaults(intent, entities)
    try:
        jql = jira_client.build_jql(intent, entities)
    except ValueError as e:
        return {"text": f"{e}\nPlease specify the missing value in your query."}

    result = await jira_client.run_query(jql, response_type=intent.get("response_type", "list"))
    issues = result.get("issues", [])
    text = summarize(user_query, issues, intent.get("response_type", "list"))
    debug = f"\n\n[debug] JQL: {jql}"
    return {"text": text + debug, "jql": jql}


