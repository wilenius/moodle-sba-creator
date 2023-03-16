import sys
import openai

openai.api_key = "YOUR API KEY HERE"

topic = str(sys.argv[1])
iterations = int(sys.argv[2])

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0301",
    messages=[
        {"role": "system", "content": "You are a helpful teacher's assistant that creates multiple choice questions based on the topics given by the user."},
        {"role": "system", "name":"example_user", "content": f"""I need you to print {iterations} separate multiple choice questions with four alternative answers, the correct answer being the fourth answer. The third answer should be close to a correct answer, but still unequivocally wrong. The topic of the question is selected based on the user input. The output format is correctly formatted Moodle Quiz XML, here's an example of the format:

        	<question type="multichoice">
			<name>
				<text>Question name</text>
			</name>
			<questiontext format="html">
				<text>Question text</text>
			</questiontext>
			<answer fraction="0">
    			<text>Alternative answer 1</text>
   				<feedback><text>Incorrect.</text></feedback>
			</answer>
			<answer fraction="0">
    			<text>Alternative answer 2</text>
   				<feedback><text>Incorrect.</text></feedback>
			</answer>
			<answer fraction="0">
				<text>Alternative answer 3</text>
				<feedback><text>Almost correct.</text></feedback>
			</answer>
			<answer fraction="100">
    			<text>Alternative answer 4</text>
   			<feedback><text>Correct.</text></feedback>
			</answer>
			</question>

			The first question topic is: history of Borneo"""
        },
        {"role": "system", "name": "example_assistant", "content": """
        	<question type="multichoice">
			<name>
				<text>History of Borneo 1</text>
			</name>
			<questiontext format="html">
				<text>When does the documented history with the island of Borneo and the imperial China begin?</text>
			</questiontext>
			<answer fraction="0">
    			<text>In the 17th century, when the sultans of Western Borneo imported laborers from China to work in mines.</text>
   				<feedback><text>Incorrect. The immigration of laborers started in the 18th century. Also, there are much earlier historical sources.</text></feedback>
			</answer>
			<answer fraction="0">
    			<text>In the 18th century, when the sultans of Western Borneo imported laborers from China to work in mines.</text>
   				<feedback><text>Incorrect. The sultans did import laborers, but there are earlier historical sources.</text></feedback>
			</answer>
			<answer fraction="0">
				<text>In the 14th century</text>
				<feedback><text>Almost correct. In the 14th century, the Sultan of Brunei changed his allegiance from Majapahit to imperial China, but there are earlier Chinese historical sources that mention the island.</text></feedback>
			</answer>
			<answer fraction="100">
    			<text>In the 9th century.</text>
   			<feedback><text>Correct. A Chinese manuscript from the year 977 mentions the island of "P'o-ni".</text></feedback>
			</answer>
			</question>"""},
        {"role": "system", "name":"user", "content": f"""Now, output {iterations} unique questions on this topic: {topic}."""},
    ],
    temperature=0,
    top_p=1,
)

result = ''
for choice in response.choices:
    result += choice.message.content

print(result)