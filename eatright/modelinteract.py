# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# from langchain.schema.runnable import RunnableLambda ,RunnableSequence
# from langchain_community.llms.ctransformers import CTransformers
# from langchain.callbacks import StreamingStdOutCallbackHandler
import re , json , requests
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

def getimg(q):
    url = 'https://www.googleapis.com/customsearch/v1'

    # Parameters for the request
    params = {
        'q': "dishes photo "+q,
        'key': os.getenv('GOOGLE_IMAGE_API_KEY'),  # Your Google API key
        'cx': os.getenv('GOOGLE_IMAGE_CX_ID'),
        'start': 3,
        'num': 1,
        'searchType': 'image',
        'imgSize': 'xlarge',  # Options: 'icon', 'small', 'medium', 'large', 'xlarge', 'xxlarge', 'huge'
        'imgType': 'photo',   # Get only photo results
        'safe': 'active'      # Safe search setting
    }

    # Making the GET request
    onresult = requests.get(url, params=params)
    result = onresult.json()
    ab = result.get("items")
    if ab:
        for i in ab:
            # Try to get thumbnail URL first, if not available use original link
            return  i.get("link")
        

def plain_text_to_json(plain_text):
    # Split the plain text into individual dish entries
    dish_entries = plain_text.split("\n")
    
    # Initialize an empty dictionary to hold the JSON data
    dishes_dict = {}
    
    for entry in dish_entries:
        # Split each entry into the number, dish name, and description
        try:
            dish_num, dish_info = entry.split(".", 1)
            dish_name, dish_description = dish_info.split("-", 1)
            
            # Populate the dictionary with the required fields
            dishes_dict[int(dish_num)] = {
                "dish_name": dish_name.strip(),
                "dish_description": dish_description.strip(),
                "dish_image": "{% static 'image.png' %}"
            }
        except ValueError:
            print(f"Entry not in expected format: {entry}")
    
    return dishes_dict

class lamba():

    def __init__(self):
        pass

    def gemini(self, bigqu,chat):
        # llm = CTransformers(
        #     model="TheBloke/Llama-2-7B-Chat-GGML", 
        #     model_file = 'C:\Programs\eatright\llama-2-7b-chat.ggmlv3.q8_0.bin', 
        #     callbacks=[StreamingStdOutCallbackHandler()]
        # )


        template = """
        [INST] <<SYS>>
        Recent Chats : {chat}

        Your are food expert , and you everything about human consumption and food.
        Your name is Eatright AI and you help people to solve their food related queries.
        you have recommend a dish if user ask for it and not for every query, 
        if you feel user is may need a dish then only recommend it, give the dish name at last of response in square bracket.
        you know everything about food and you are very good at it.
        if user ask anything beyond food then say "Its beyond my scope".


        Input : {prompt}[/INST]
        """

        # prompt = PromptTemplate(template=template, input_variables=["prompt"])

        # pipeline = RunnableSequence(prompt, llm)

        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))  # Set your Google API key
        prompt = template.format(chat=chat , prompt=bigqu)
        model = genai.GenerativeModel('gemini-1.5-flash')  # Adjust model as needed
        response = model.generate_content(prompt)
        
        # Extract text inside square brackets and clean the response
        pattern = r'\[(.*?)\]'
        response_text = response.text.strip()
        
        # Find recommendation (text in square brackets)
        recommendation = re.findall(pattern, response_text)
        recommendation = recommendation[0] if recommendation else None
        
        # Remove the square brackets and text inside them
        clean_text = re.sub(pattern, '', response_text).strip()
        
        return {
            'response': clean_text,
            'recommendation': getimg(recommendation) if recommendation else None,
        }


    def gemma(self,bigqu: str, chat_history=""):


        try:
            reqUrl = "http://localhost:8585/chat"
            headersList = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            # Prepare payload with escaped newlines
            payload = {
                "prompt": bigqu,
                "chat_history": chat_history ,
            }

            # Make request
            response = requests.post(
                reqUrl,
                json=payload,
                headers=headersList
            )
            
            # Check for successful response
            response.raise_for_status()
            result = response.json()


            return {
                'response': result.get('response', ''),
                'recommendation': getimg(result.get('suggestion')) if result.get('suggestion') else None,
                'status': 'success'
            }

        except requests.RequestException as e:
            print(e)
            return {
                'response': f"API Error: {str(e)}",
                'recommendation': None,
                'image_url': None,
                'status': 'error'
            }
        except Exception as e:
            return {
                'response': f"Processing Error: {str(e)}",
                'recommendation': None,
                'image_url': None,
                'status': 'error'
            }

    # Example usage
    if __name__ == "__main__":
        # Test the function
        question = "What should I eat for breakfast?"
        previous_chat = [
            {
                "user": "I want to eat healthy",
                "response": "Focus on protein-rich foods [Oatmeal]",
                "image": "http://example.com/oatmeal.jpg"
            }
        ]
        
        result = gemma(question, previous_chat)
        print(json.dumps(result, indent=2))
#for testing purpose
# obj = lamba()
# print(obj.llama7b("cheese burgers"))


