from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from food_image_analyser import FoodImageAnalyser

from dotenv import load_dotenv


load_dotenv()

class NutritionistAgent:
    def __init__(self, session_id, db_path='sqlite://memmory.db') -> None:
        self.llm =  ChatOpenAI(
            model="gp-3.5-turbo",
            temperature=0.1
            )
        
        system_prompt = '''
            Backstory:
            Esse agente é uma referência global no campo da nutrição, apelidado de "Nutricionista do Futuro" ou "Nutricionista 2.0". Ele é um especialista em nutrição e saúde, com conhecimento profundo sobre os efeitos dos alimentos no corpo humano. Ele é capaz de fornecer informações precisas e personalizadas sobre dietas, nutrição e saúde com base em informações fornecidas pelos usuários. 

            Expected result: 
            O agente deve ter um conhecimento profundo sobre nutrição e saúde, ser capaz de fornecer informações precisas e personalizadas sobre dietas e saúde com base em informações fornecidas pelos usuários, e ser capaz de responder a perguntas sobre nutrição e saúde de forma clara e concisa.      
        '''

        self.chat_history = SQLChatMessageHistory(
            session_id=session_id,
            connection=db_path
        )

        self.memory = ConversationBufferMemory(
            memory_key='chat_memory',
            chat_memory=self.chat_history,
            return_messages=True
        )

        self.agent = initialize_agent(
            llm=self.llm,
            tools=[FoodImageAnalyser()],
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,  
            memory=self.memory,
            agent_kwargs={
                'system_massage': system_prompt
            }       
        )

    def run(self, input_text):
        try:
            response = self.agent.run(input_text)
            print(f'Agent response: {response}')
            return response
        except Exception as err:
            print(f'Error: {err}')
            return 'Desculpe, não consegui entender a sua pergunta. Poderia reformular por favor?'
            