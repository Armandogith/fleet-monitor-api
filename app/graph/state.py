from typing import TypedDict, List, Annotated
import operator

class GraphState(TypedDict):
    batch_id: str
    pending_tasks: List[dict]
    send_results: Annotated[List[dict], operator.add]