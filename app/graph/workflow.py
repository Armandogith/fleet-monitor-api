from langgraph.graph import StateGraph, END, START
from langgraph.constants import Send
from app.graph.state import GraphState
from app.graph.nodes import fetch_expiring_docs, send_sms_alert, persist_and_cleanup  # ← atualizado

def map_reduce_send(state: GraphState):
    if not state.get("pending_tasks"):
        return END
    return [Send("send_sms_alert", {"task": task}) for task in state["pending_tasks"]]  # ← atualizado

app_workflow = None

def create_workflow():
    global app_workflow
    if app_workflow is not None:
        return app_workflow

    workflow = StateGraph(GraphState)

    workflow.add_node("fetch_expiring_docs", fetch_expiring_docs)
    workflow.add_node("send_sms_alert", send_sms_alert)           # ← era send_whatsapp_alert
    workflow.add_node("persist_and_cleanup", persist_and_cleanup)

    workflow.add_edge(START, "fetch_expiring_docs")
    workflow.add_conditional_edges(
        "fetch_expiring_docs",
        map_reduce_send,
        ["send_sms_alert", END]                                   # ← era send_whatsapp_alert
    )
    workflow.add_edge("send_sms_alert", "persist_and_cleanup")
    workflow.add_edge("persist_and_cleanup", END)

    app_workflow = workflow.compile()
    return app_workflow