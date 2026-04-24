from langgraph.graph import StateGraph, END, START
from langgraph.constants import Send
from app.graph.state import GraphState
from app.graph.nodes import fetch_expiring_docs, send_whatsapp_alert, persist_and_cleanup

def map_reduce_send(state: GraphState):
    # Se não houver documentos vencendo, encerra o processo
    if not state.get("pending_tasks"):
        return END
    # Para cada documento, dispara a tarefa de enviar WhatsApp paralelamente
    return [Send("send_whatsapp_alert", {"task": task}) for task in state["pending_tasks"]]

app_workflow = None

def create_workflow():
    global app_workflow
    if app_workflow is not None:
        return app_workflow
        
    workflow = StateGraph(GraphState)
    
    # Adiciona os nós (etapas)
    workflow.add_node("fetch_expiring_docs", fetch_expiring_docs)
    workflow.add_node("send_whatsapp_alert", send_whatsapp_alert)
    workflow.add_node("persist_and_cleanup", persist_and_cleanup)
    
    # Define o fluxo
    workflow.add_edge(START, "fetch_expiring_docs")
    workflow.add_conditional_edges("fetch_expiring_docs", map_reduce_send, ["send_whatsapp_alert", END])
    workflow.add_edge("send_whatsapp_alert", "persist_and_cleanup")
    workflow.add_edge("persist_and_cleanup", END)
    
    app_workflow = workflow.compile()
    return app_workflow