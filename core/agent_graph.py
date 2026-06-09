"""
LangGraph 多 Agent 协作图
使用状态图管理 Agent 之间的流转和协作
"""
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import operator


# ==================== 状态定义 ====================

class AgentState(TypedDict):
    """LangGraph 状态定义

    使用 Annotated 实现消息的累加（而非覆盖）
    """
    # 消息历史（累加）
    messages: Annotated[List[Dict], add_messages]

    # 用户输入
    user_message: str

    # 用户档案
    user_profile: Dict[str, Any]

    # 路由结果
    primary_agent: str
    secondary_agents: List[str]
    intent: str
    emotion: str
    emotion_intensity: float
    reasoning: str
    is_switch: bool

    # 协作上下文
    collaboration_input: str

    # 最终响应
    final_response: str

    # 当前步骤（用于调试）
    current_step: str


# ==================== 节点函数 ====================

def create_graph_nodes(llm, agents: Dict, agent_info: Dict, memory_manager=None):
    """创建 LangGraph 节点函数

    Args:
        llm: LangChain LLM 实例
        agents: Agent 实例字典
        agent_info: Agent 信息字典（用于UI）
        memory_manager: 记忆管理器实例

    Returns:
        节点函数字典
    """

    async def analyze_intent(state: AgentState) -> Dict:
        """意图分析节点 - 使用 LLM 分析用户意图"""
        message = state["user_message"]
        user_profile = state.get("user_profile", {})

        # 检查是否是切换 Agent 请求
        switch_keywords = {
            "鹅厂专家": "tencent_expert",
            "腾讯专家": "tencent_expert",
            "面试教练": "interview_coach",
            "面试官": "interview_coach",
            "情绪树洞": "emotional_supporter",
            "战术导师": "career_navigator",
            "职业导师": "career_navigator",
        }

        is_switch = False
        primary_agent = "career_navigator"

        for keyword, agent_id in switch_keywords.items():
            if keyword in message and any(kw in message for kw in ["切换", "转换", "换成", "用"]):
                primary_agent = agent_id
                is_switch = True
                break

        if is_switch:
            return {
                "primary_agent": primary_agent,
                "secondary_agents": [],
                "intent": "切换Agent",
                "emotion": "normal",
                "emotion_intensity": 0,
                "reasoning": f"用户请求切换Agent",
                "is_switch": True,
                "current_step": "intent_analyzed",
            }

        # 使用 LLM 进行意图分析
        routing_prompt = f"""分析用户消息，判断应该由哪个专家Agent来回应。

用户消息: {message}

用户背景:
- 年级: {user_profile.get('grade_name', '大学生')}
- 专业: {user_profile.get('major', '未知')}
- 目标: {user_profile.get('target', '未设置')}

可选的专家Agent:
1. career_navigator (战术导航导师) - 职业规划、技术学习、能力提升
2. emotional_supporter (情绪树洞) - 情绪倾诉、压力疏导、心理支持
3. interview_coach (面试教练) - 面试准备、简历优化、模拟面试
4. tencent_expert (鹅厂专家) - 腾讯业务、岗位解读、企业文化

请以JSON格式返回分析结果:
{{
    "primary_agent": "主要负责的agent名称",
    "secondary_agents": ["辅助协作的agent列表"],
    "intent": "用户意图描述",
    "emotion": "情绪状态(normal/anxious/frustrated/excited)",
    "emotion_intensity": 0.0-1.0,
    "reasoning": "路由理由"
}}

只返回JSON，不要其他内容。"""

        try:
            import json
            response = await llm.ainvoke([HumanMessage(content=routing_prompt)])
            content = response.content

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())

            # 验证 agent 名称
            valid_agents = ["career_navigator", "emotional_supporter", "interview_coach", "tencent_expert"]
            if result.get("primary_agent") not in valid_agents:
                result["primary_agent"] = "career_navigator"
            result["secondary_agents"] = [a for a in result.get("secondary_agents", []) if a in valid_agents]

            return {
                "primary_agent": result.get("primary_agent", "career_navigator"),
                "secondary_agents": result.get("secondary_agents", []),
                "intent": result.get("intent", ""),
                "emotion": result.get("emotion", "normal"),
                "emotion_intensity": result.get("emotion_intensity", 0),
                "reasoning": result.get("reasoning", ""),
                "is_switch": False,
                "current_step": "intent_analyzed",
            }
        except Exception as e:
            # 降级到默认路由
            return {
                "primary_agent": "career_navigator",
                "secondary_agents": [],
                "intent": "general",
                "emotion": "normal",
                "emotion_intensity": 0,
                "reasoning": f"降级路由: {str(e)}",
                "is_switch": False,
                "current_step": "intent_analyzed",
            }

    async def update_memory(state: AgentState) -> Dict:
        """记忆更新节点"""
        if not memory_manager:
            return {"current_step": "memory_updated"}

        message = state["user_message"]
        emotion = state.get("emotion", "normal")
        emotion_intensity = state.get("emotion_intensity", 0)

        # 记录情绪
        if emotion_intensity >= 0.3:
            await memory_manager.record_emotion(emotion, emotion_intensity, message)

        return {"current_step": "memory_updated"}

    async def gather_collaboration(state: AgentState) -> Dict:
        """协作收集节点 - 收集辅助 Agent 的建议"""
        secondary_agents = state.get("secondary_agents", [])

        if not secondary_agents:
            return {"collaboration_input": "", "current_step": "collaboration_gathered"}

        message = state["user_message"]
        collaboration_inputs = []

        for agent_name in secondary_agents[:2]:
            agent = agents.get(agent_name)
            if agent:
                collab_prompt = f"""作为协作专家，请针对用户问题提供简短的专业建议（50字以内）：
用户问题: {message}
你的角色: {agent_info.get(agent_name, {}).get('name', agent_name)}"""

                try:
                    response = await llm.ainvoke([
                        SystemMessage(content=agent.build_system_prompt(agent.SYSTEM_PROMPT if hasattr(agent, 'SYSTEM_PROMPT') else "")),
                        HumanMessage(content=collab_prompt)
                    ])
                    collaboration_inputs.append({
                        "agent_name": agent_info.get(agent_name, {}).get('name', agent_name),
                        "suggestion": response.content[:100],
                    })
                except:
                    pass

        if collaboration_inputs:
            collaboration_text = "\n".join([
                f"[{inp['agent_name']}建议]: {inp['suggestion']}"
                for inp in collaboration_inputs
            ])
            return {"collaboration_input": collaboration_text, "current_step": "collaboration_gathered"}

        return {"collaboration_input": "", "current_step": "collaboration_gathered"}

    async def route_to_agent(state: AgentState) -> Dict:
        """Agent 路由节点 - 根据意图路由到对应 Agent"""
        primary_agent = state.get("primary_agent", "career_navigator")

        # 返回下一个节点名称
        return primary_agent

    async def execute_career_navigator(state: AgentState) -> Dict:
        """执行战术导航导师"""
        return await _execute_agent("career_navigator", state, agents, agent_info)

    async def execute_emotional_supporter(state: AgentState) -> Dict:
        """执行情绪树洞"""
        return await _execute_agent("emotional_supporter", state, agents, agent_info)

    async def execute_interview_coach(state: AgentState) -> Dict:
        """执行面试教练"""
        return await _execute_agent("interview_coach", state, agents, agent_info)

    async def execute_tencent_expert(state: AgentState) -> Dict:
        """执行鹅厂专家"""
        return await _execute_agent("tencent_expert", state, agents, agent_info)

    async def generate_switch_response(state: AgentState) -> Dict:
        """生成切换响应"""
        primary_agent = state.get("primary_agent", "career_navigator")
        info = agent_info.get(primary_agent, {})

        response = f"""好的，已收到切换指令。现在我将以 **{info.get('icon', '🤖')} {info.get('name', 'AI助手')}** 的身份与你对话。

{info.get('description', '')}

请告诉我你想了解什么？"""

        return {"final_response": response, "current_step": "completed"}

    return {
        "analyze_intent": analyze_intent,
        "update_memory": update_memory,
        "gather_collaboration": gather_collaboration,
        "route_to_agent": route_to_agent,
        "career_navigator": execute_career_navigator,
        "emotional_supporter": execute_emotional_supporter,
        "interview_coach": execute_interview_coach,
        "tencent_expert": execute_tencent_expert,
        "generate_switch_response": generate_switch_response,
    }


async def _execute_agent(agent_name: str, state: AgentState, agents: Dict, agent_info: Dict) -> Dict:
    """执行指定 Agent 并返回响应"""
    agent = agents.get(agent_name)
    if not agent:
        return {"final_response": "抱歉，对应的专家暂时不可用。", "current_step": "completed"}

    message = state["user_message"]
    user_profile = state.get("user_profile", {})
    collaboration_input = state.get("collaboration_input", "")

    # 构建上下文
    context = {
        "grade_name": user_profile.get("grade_name", "大学生"),
        "major": user_profile.get("major", ""),
        "target": user_profile.get("target", ""),
        "interests": user_profile.get("interests", []),
        "skills": user_profile.get("skills", []),
        "emotion": state.get("emotion", "normal"),
        "emotion_intensity": state.get("emotion_intensity", 0),
        "collaboration_input": collaboration_input,
    }

    # 执行 Agent
    response_text = ""
    async for chunk in agent.process(message, context, None):
        response_text += chunk

    return {"final_response": response_text, "current_step": "completed"}


# ==================== 构建图 ====================

def build_agent_graph(llm, agents: Dict, agent_info: Dict, memory_manager=None) -> StateGraph:
    """构建 LangGraph 多 Agent 协作图

    图结构:

    START → analyze_intent → update_memory → gather_collaboration
                                                       ↓
                                              route_to_agent
                                                       ↓
                    ┌──────────┬──────────┼──────────┬──────────┐
                    ↓          ↓          ↓          ↓          ↓
              career_nav  emotional  interview  tencent   switch_response
                    └──────────┴──────────┴──────────┴──────────┘
                                       ↓
                                     END
    """
    # 创建节点函数
    nodes = create_graph_nodes(llm, agents, agent_info, memory_manager)

    # 创建状态图
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("analyze_intent", nodes["analyze_intent"])
    graph.add_node("update_memory", nodes["update_memory"])
    graph.add_node("gather_collaboration", nodes["gather_collaboration"])
    graph.add_node("career_navigator", nodes["career_navigator"])
    graph.add_node("emotional_supporter", nodes["emotional_supporter"])
    graph.add_node("interview_coach", nodes["interview_coach"])
    graph.add_node("tencent_expert", nodes["tencent_expert"])
    graph.add_node("generate_switch_response", nodes["generate_switch_response"])

    # 设置入口
    graph.set_entry_point("analyze_intent")

    # 添加边：意图分析 → 记忆更新
    graph.add_edge("analyze_intent", "update_memory")

    # 添加条件边：记忆更新 → 协作收集 或 直接响应切换
    def after_memory(state: AgentState) -> str:
        if state.get("is_switch"):
            return "switch"
        return "continue"

    graph.add_conditional_edges(
        "update_memory",
        after_memory,
        {
            "switch": "generate_switch_response",
            "continue": "gather_collaboration",
        }
    )

    # 添加边：协作收集 → Agent 执行（条件路由）
    def route_to_agent_node(state: AgentState) -> str:
        return state.get("primary_agent", "career_navigator")

    graph.add_conditional_edges(
        "gather_collaboration",
        route_to_agent_node,
        {
            "career_navigator": "career_navigator",
            "emotional_supporter": "emotional_supporter",
            "interview_coach": "interview_coach",
            "tencent_expert": "tencent_expert",
        }
    )

    # 所有 Agent 节点 → END
    graph.add_edge("career_navigator", END)
    graph.add_edge("emotional_supporter", END)
    graph.add_edge("interview_coach", END)
    graph.add_edge("tencent_expert", END)
    graph.add_edge("generate_switch_response", END)

    return graph


# ==================== 编译图 ====================

def compile_agent_graph(llm, agents: Dict, agent_info: Dict, memory_manager=None):
    """编译并返回可执行的 LangGraph"""
    graph = build_agent_graph(llm, agents, agent_info, memory_manager)
    return graph.compile()


# ==================== 测试代码 ====================

if __name__ == "__main__":
    import asyncio

    async def test_graph():
        """测试 LangGraph 多 Agent 协作"""
        from langchain_openai import ChatOpenAI
        import os

        # 初始化 LLM
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
        )

        # 模拟 Agent（简化版）
        class MockAgent:
            def __init__(self, name):
                self.name = name
                self.SYSTEM_PROMPT = f"You are {name}"

            def build_system_prompt(self, base):
                return base

            async def process(self, message, context, history):
                yield f"[{self.name}] 收到消息: {message}"

        agents = {
            "career_navigator": MockAgent("career_navigator"),
            "emotional_supporter": MockAgent("emotional_supporter"),
            "interview_coach": MockAgent("interview_coach"),
            "tencent_expert": MockAgent("tencent_expert"),
        }

        agent_info = {
            "career_navigator": {"name": "战术导航导师", "icon": "🧭"},
            "emotional_supporter": {"name": "情绪树洞", "icon": "💝"},
            "interview_coach": {"name": "面试教练", "icon": "🎯"},
            "tencent_expert": {"name": "鹅厂专家", "icon": "🐧"},
        }

        # 编译图
        compiled_graph = compile_agent_graph(llm, agents, agent_info)

        # 测试输入
        test_input = {
            "messages": [],
            "user_message": "腾讯2025校招什么时候开始？",
            "user_profile": {"grade_name": "大三", "major": "计算机"},
        }

        # 执行图
        result = await compiled_graph.ainvoke(test_input)

        print("最终响应:", result.get("final_response"))
        print("路由到的Agent:", result.get("primary_agent"))
        print("意图:", result.get("intent"))

    asyncio.run(test_graph())