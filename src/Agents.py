from langchain.agents import AgentExecutor,create_tool_calling_agent,create_structured_chat_agent
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_core.runnables import ConfigurableField
from .Prompt import PromptClass
from .Memory import MemoryClass
from .Emotion import EmotionClass
from langchain_core.caches import InMemoryCache
from .Storage import get_user

from .Tools import search,get_info_from_local,create_todo,checkSchedule,SetSchedule,SearchSchedule,ModifySchedule,DelSchedule,ConfirmDelSchedule
from dotenv import load_dotenv as _load_dotenv
_load_dotenv()
import os
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("OPENAI_API_BASE")
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")
os.environ["DEEPSEEK_API_BASE"] = os.getenv("DEEPSEEK_API_BASE")
#添加缓存
from langchain_core.globals import set_llm_cache
set_llm_cache(InMemoryCache())

class AgentClass:
    """AI代理类，负责处理用户输入并生成回复 整合语言模型、记忆系统、情感分析和各种工具"""

    def __init__(self):
        fallabck_llm = ChatDeepSeek(model=os.getenv("BACKUP_MODEL"))

        self.modelname = os.getenv("BASE_MODEL")

        self.chatmodel = ChatOpenAI(model=self.modelname).with_fallbacks([fallabck_llm])

        self.tools = [search,get_info_from_local,create_todo,checkSchedule,SetSchedule,SearchSchedule,ModifySchedule,ConfirmDelSchedule,DelSchedule]

        self.memorykey = os.getenv("MEMORY_KEY")

        self.feeling = {"feeling":"default","score":5}

        self.prompt = PromptClass(memorykey=self.memorykey,feeling=self.feeling).Prompt_Structure()

        self.memory = MemoryClass(memorykey=self.memorykey,model=self.modelname)

        self.emotion = EmotionClass(model=self.modelname)
        
        self.agent = create_tool_calling_agent(
            self.chatmodel,
            self.tools,
            self.prompt
        )

        self.agent_chain = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory.set_memory(),
            verbose=True
        ).configurable_fields(
            memory=ConfigurableField(
                id="agent_memory",
                name="Agent Memory",
                description="The memory of the agent"
            )
        )
    def run_agent(self,input):
        """运行AI处理用户输入 
        参数：
            input：用户输入的文本
            
        返回
            包含AI回复的字典"""
        
        self.feeling = self.emotion.Emotion_Sensing(input)

        self.prompt = PromptClass(memorykey=self.memorykey,feeling=self.feeling).Prompt_Structure()

        print("self.prompt",self.prompt)

        res = self.agent_chain.with_config(
            {
                "agent_memory":self.memory.set_memory(session_id=get_user("userid"))
            }
        ).invoke(
            {"input":input}
        )
        return res


