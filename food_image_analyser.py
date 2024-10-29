import base64
from io import BytesIO
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage    
from langchain_openai import ChatOpenAI
from PIL import Image


class FoodImageAnalyser(BaseTool):
    name: str = 'food_mage_analyser'
    description: str = '''
    Ultilize esta ferramente para analisar pratos de comida que o usuário enviar. Descreva os alimentos presentes e crie uma tabela nutricional da refeição. O agente deve usar esta ferramenta sempre que o caminho da imagem for fornecido, mas somente quando o input for um caminho de imagem.
    '''
    
    def __init__(self):
        super().__init__()

    def run(self, image_path: str):
       image = Image.open(image_path)
       buffered = BytesIO()
       image.save(buffered, format='JPEG')
       img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

       instructions = '''
       Voce Deve analaisar a imagem enviada e verificar se ela contem um prato de comida.
       Caso seja um prato de comida, descreva os intens visies no prato e crie uma descrição nutricional detalhada e estemida incluindo todos os macronutristentes e calorias. Forneça uma descrição detalhada completa da refeição.   
       '''

       llm = ChatOpenAI(model='gp-3.5-turbo')
       message = [HumanMessage(
          content=[
              {'type': 'text', 'text': instructions},
              {'type': 'image_url', 'image_url': {'url': f"data:image/jpeg;base64,{img_b64}"}}
            ]	
        )]
       
       response = llm.invoke(message)
       return response
    
    async def _arun(self, image_path: str) -> str:
        raise NotImplementedError('Execução assíncrona não suportada')