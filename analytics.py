from server import app, db, TestingResult, GPTPricer, decrypt
import time
import json
import openai
import datetime
from dotenv import dotenv_values
from requests.exceptions import HTTPError

config = dotenv_values(".env") 
MAX_TOKENS = int(config['MAX_TOKENS'])
INPUT_COST_PER_1K_TOKENS = float(config['INPUT_COST_PER_1K_TOKENS'])
OUTPUT_COST_PER_1K_TOKENS = float(config['OUTPUT_COST_PER_1K_TOKENS'])
API_KEY_OPENAI = config['API_KEY_OPENAI']

def compute_request_cost(result):
    """
    Calculates how many tokens were spent (incoming, outgoing), and returns the price in USD of how many tokens were spent for 1 request.
    """

    input_tokens = result['usage']['prompt_tokens']
    output_tokens = result['usage']['completion_tokens']
    input_cost = (input_tokens / 1000) * INPUT_COST_PER_1K_TOKENS
    output_cost = (output_tokens / 1000) * OUTPUT_COST_PER_1K_TOKENS
    total_cost = input_cost + output_cost
    
    return total_cost

def is_json(content):
    try:
        json.loads(content)
        return True
    except json.JSONDecodeError:
        return False

def get_input_tokens_count(messages):
    """
    Number of tokens spent
    """
    
    return sum([len(message["content"].split()) for message in messages])

def get_prompt_result(messages):
    conter_iter = 0
    total_input_tokens = get_input_tokens_count(messages)
    available_tokens_for_response = MAX_TOKENS - total_input_tokens
    if available_tokens_for_response <= 0:
        print("Warning: Input messages are too long, reducing available tokens for response.")
        available_tokens_for_response = MAX_TOKENS // 2

    openai.api_key = API_KEY_OPENAI
    while True:
        conter_iter += 1
        try:
            if conter_iter >= 5:
                return False
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=messages,
                temperature=0.3,
                max_tokens=available_tokens_for_response,
                stop=None,
                n=1,
                presence_penalty=0.8,
                frequency_penalty=0.2
            )

            cost = compute_request_cost(result)
            message = result['choices'][0]['message']['content']

            try:
                response_json = json.loads(message)
                print(response_json)
                return response_json, cost
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {str(e)}")
                time.sleep(5)
                continue

        except HTTPError as e:
            print('HTTP Error during OpenAI call: ', e)
            time.sleep(10)
            continue
        except Exception as e:
            print('Error during OpenAI call or parsing: ', e)
            time.sleep(10)
            continue

def analyze_answers(arr_step):
    while True:
        try:
            schema = {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "data": "The question you're writing a recommendation for from the list"},
                    "recommendation": {"type": "string", "data": "The recommendations you're making"},
                    "satisfaction": "exaple 54.3"
                }
            }
            
            messages_q1 = [
                {"role": "system", "content": f"""
                    You are a helpful assistant. You need to analyze the questions and the answer, 
                    give as json in no extra words, just json format {schema}. JSON keys should be double-quoted ("), 
                    not single-quoted ("). It is important that the answer cannot exceed 5,000 tokens. 
                    in key 'satisfaction' add percentage of satisfaction from 0 to 100 percent based on user response. There must be a number, if a non-generic user has made a review, it means the percentage of satisfaction with the work, less
                """},
                {"role": "user", "content": f"""
                    I will provide an array of answers and questions, this was answered by a company worker, 
                    he may no longer be working. But we are interested in the result of the analysis. 
                    You need to analyze the question and answer and give it as json in {schema}. 
                    You can't write that this answer is not relevant! 
                    It is better to just write recommendations for improvement in the company based on the question. 
                    Just your opinion on how to improve, if even the answer to the question is not relevant. 
                    If it is a positive feedback, then write that your employee likes it, etc. 
                    If the answer is not relevant to the question, then you should just write in recommendations, 
                    just from yourself how you can improve the company based on the question. 
                    You can't say that the answer is not relevant. This will be read by business owners. 
                    That is, from each question we should get a squeeze of recommendations on what is best to do 
                    to make the company's workers or teams more comfortable to work.  
                    It is important to remember that the answer may not be relevant to the question, 
                    if it is, and the answer has nothing to do with the company. 
                    But it should be returned as a simple recommendation for the company on how to improve performance 
                    or this or that based on the question. \n\n 
                    Satisfaction - percentage of satisfaction from 0 to 100 percent based on user response.
                    There must be a number, if a non-generic user has made a review, it means the percentage of satisfaction with the work, less.
                    Here are the questions and answers to analyze: \n {arr_step}
                """}
            ]

            total_input_tokens = get_input_tokens_count(messages_q1)
            available_tokens_for_response = MAX_TOKENS - total_input_tokens
            if available_tokens_for_response <= 0:
                print("Warning: Input messages are too long, reducing available tokens for response.")
                available_tokens_for_response = MAX_TOKENS // 2

            openai.api_key = API_KEY_OPENAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=messages_q1,
                max_tokens=available_tokens_for_response,
                stop=None
            )
            answer = response['choices'][0]['message']['content']
            
            result = json.loads(answer)
            cost = compute_request_cost(response)
            result = result['properties']
            return result, cost
        except Exception as e:
            print(e)
            continue

def sumarizator_gpt(results):
    while True:
        try:
            schema = {
                "type": "object",
                "properties": {
                    "summation_result": {"type": "string", "data": "Here is a text for the owner of the company, what should be done to improve the quality of work in the team and in general in the workplace"},
                }
            }
            messages_q1 = [
                {"role": "system", "content": f"""
                    You are a helpful assistant. JSON keys should be double-quoted (\\"\\"), not single-quoted ('). It is important that the answer cannot exceed 5,000 tokens. The response should be returned immediately in JSON form: {schema}
                """},
                {"role": "user", "content": f"""
                I give an array of questions and recommendations on what a business owner needs to do to make it easier for employees to work. JSON keys should be enclosed in double quotes (""), not single quotes (""). It is desirable to describe point by point, not just a bunch of recommendations. It is necessary to analyze and summarize, explain what and how to do better to make employees feel comfortable working in the company, it is forbidden to say that some of the requests are not relevant, it is necessary to give recommendations on how to make employees feel comfortable working. 
                This is how the json in the response should look like: {schema}
                Here is an array for analysis: \n {results}
                """}
            ]

            total_input_tokens = get_input_tokens_count(messages_q1)
            available_tokens_for_response = MAX_TOKENS - total_input_tokens
            if available_tokens_for_response <= 0:
                print("Warning: Input messages are too long, reducing available tokens for response.")
                available_tokens_for_response = MAX_TOKENS // 2

            openai.api_key = API_KEY_OPENAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=messages_q1,
                max_tokens=available_tokens_for_response,
                stop=None
            )
            answer = response['choices'][0]['message']['content']
            
            result = json.loads(answer)
            cost = compute_request_cost(response)
            result = result['properties']
            return result, cost
        except Exception as e:
            print(e)
            continue

def background_scan():
    """
    Scanning the database for unanswered ChatGPT questionnaires, after scanning it will mark in the database that it has already read it and the answer has been given.
    """

    data = TestingResult.query.filter_by(checked=False).all()
    for item in data:
        print(item)
        array = json.loads(item.user_answer)
        results = []
        count_price = 0
        for arr in array:
            try:
                question = arr['question']
                text = decrypt(arr['text'])
                arr_step = {"question": question, "text": text}
                result, count = analyze_answers(arr_step)
                if result == False:
                    continue
                print(result)
                
                count_price = count_price + count
                results.append(result)
            except Exception as e:
                print(e)
                continue

        if len(results) == 0:
            continue

        print("Count price: ", count_price)

        # Average satisfaction value
        total_satisfaction = 0
        new_array = []
        count = 0
        for sat in results:
            print(sat)
            sat_value = sat['satisfaction']
            if not sat_value:
                sat_value = 0
            sat_value = str(sat_value).replace("%", "")
            obj = {
                "question": sat['question']['data'],
                "recommendation": sat['recommendation']['data'],
                "satisfaction": sat['satisfaction']
            }
            new_array.append(obj)
            try:
                total_satisfaction += float(sat_value)
                count += 1
            except ValueError:
                print(f"Error converting satisfaction value '{sat_value}' to float")

        average_satisfaction = total_satisfaction / count if count else 0
        print(f"Average satisfaction: {average_satisfaction:.2f}%")
        print("Суммировине результатов")
        summation_result, count = sumarizator_gpt(new_array)
        print(summation_result)
        count_price += count

        data = []
        data.append({"result": new_array})
        data.append({"summation": summation_result})
        data.append({"satisfaction": f"{average_satisfaction:.2f}%"})

        res = TestingResult.query.filter_by(id=item.id).first()
        res.result = json.dumps(data)
        res.checked = True
        db.session.commit()

        # price_db = GPTPricer(public_id=item.public_id, price_count=count_price, timestamp=datetime.datetime.utcnow())
        # db.session.add(price_db)
        # db.session.commit()

        print('Done')
    print('Over!')

if __name__ == '__main__':
    while True:
        with app.app_context():
            background_scan()
            time.sleep(60)