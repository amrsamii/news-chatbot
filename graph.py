from typing import Optional

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.runnables.utils import Input, Output
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import Annotated, TypedDict, override


class NewsGraphState(TypedDict):
    """State for the NewsGraph."""

    messages: Annotated[BaseMessage, add_messages]


class NewsGraph(Runnable):
    """A graph that processes user queries and gathers content from a website."""

    AGENT_NODE_NAME = "agent"
    TOOLS_NODE_NAME = "tools"

    def __init__(self, llm, tools):
        self._llm = llm
        self._tools = tools
        self._graph = self._create_graph()

    def _create_graph(self):
        workflow = StateGraph(NewsGraphState)
        workflow.add_node(self.AGENT_NODE_NAME, self._call_agent)
        workflow.add_node(self.TOOLS_NODE_NAME, ToolNode(self._tools))
        workflow.add_edge(START, self.AGENT_NODE_NAME)
        workflow.add_conditional_edges(self.AGENT_NODE_NAME, tools_condition)
        workflow.add_edge(self.TOOLS_NODE_NAME, self.AGENT_NODE_NAME)
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)

    def _call_agent(self, state: NewsGraphState):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are a helpful assistance.
                    Your task is to process the user query,
                    gather content from a website and summarize the content based on the specified category.
                    There are two websites the user can choose from: the BBC website and the Guardian website.
                    The BBC categories are:
                    - sport
                    - business
                    - innovation
                    - culture
                    - arts
                    - travel
                    The Guardian categories are:
                    - sport
                    - business
                    - culture
                    - artanddesign
                    - travel
                    """,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        runnable = prompt | self._llm
        response = runnable.invoke(state)
        return {"messages": [response]}

    @override
    def invoke(self, input: Input, config: Optional[RunnableConfig] = None) -> Output:
        config = {"configurable": {"thread_id": "1"}}
        final_state = self._graph.invoke({"messages": [HumanMessage(input["user_prompt"])]}, config=config)
        return final_state["messages"][-1].content
