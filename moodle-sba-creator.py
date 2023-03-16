import sys
import openai
from pathlib import Path
import traceback
import logging

# PARAMETERS: 1. topic file (list of question topics separated by newline) 2. Number of questions per topic 3. name of output xml file
# Additionally, sample_question.txt for a question to prime the gpt api. If the file doesn't exist, the default sample question is used instead.

topicfile = str(sys.argv[1])
openai.api_key = "API KEY HERE"

topics = Path(topicfile).read_text()
topics_list = topics.split("\n")
xml_header = '<?xml version="1.0"?>\n<quiz>\n'

iterations = int(sys.argv[2])

sample_question_file = Path("sample_question.txt")

if sample_question_file.is_file():
    sample_question = Path(sample_question_file).read_text()
    print("Custom sample question file found, using it to generate questions.")
else:
    sample_question = """
		<question type="multichoice">
				<name>
					<text>Borneon historia 1</text>
				</name>
				<questiontext format="html">
					<text>Milloin alkaa dokumentoitu historia Borneon saaren ja Kiinan valtakunnan välillä?</text>
				</questiontext>
				<answer fraction="0">
					<text>1600-luvulla, kun Länsi-Borneon sulttaanit toivat työläisiä Kiinasta työskentelemään kaivoksissa.</text>
						<feedback><text>Väärin. Työläisten maahanmuutto Kiinasta alkoi 1700-luvulla. Lisäksi on olemassa myös aikaisempia historiallisia lähteitä.</text></feedback>
				</answer>
				<answer fraction="0">
					<text>1700-luvulla, kun Länsi-Borneon sulttaanit toivat työläisiä Kiinasta työskentelemään kaivoksissa.</text>
						<feedback><text>Väärin. Työläisten maahanmuutto Kiinasta alkoi 1700-luvulla, mutta on olemassa myös aikaisempia historiallisia lähteitä.</text></feedback>
				</answer>
				<answer fraction="0">
					<text>1300-luvulla</text>
					<feedback><text>Melkein oikein. 1300-luvulla Brunein sulttaani vaihtoi uskollisuutensa Majapahitista Kiinan valtakuntaan, mutta on olemassa varhaisempiakin kiinalaisia historiallisia lähteitä, jotka mainitsevat Borneon.</text></feedback>
				</answer>
				<answer fraction="100">
					<text>800-luvulla</text>
					<feedback><text>Oikein. Kiinalainen käsikirjoitus vuodelta 977 mainitsee saaren nimeltä "P'o-ni".</text></feedback>
				</answer>
		</question>
    """
    print("Sample question file not found. Using the default sample question")

filepath = Path(sys.argv[3])
with filepath.open("w", encoding ="utf-8") as f:
    f.write(xml_header)
    f.close()

for topic in topics_list:
	print("Generating questions for topic: " + topic)
	try:
		response = openai.ChatCompletion.create(
		    model="gpt-3.5-turbo-0301",
		    messages=[
		        {"role": "system", "content": "You are a helpful teacher's assistant that creates multiple choice questions based on the topics given by the user. You communicate in the Finnish language"},
		        {"role": "system", "name":"example_user", "content": f"""Haluan, että tulostat {iterations} erillistä monivalintakysymystä, joissa on neljä vaihtoehtoista vastausta. Neljäs vastaus on oikea vastaus. Kolmas vastaus on lähellä oikeaa vastausta, mutta silti yksiselitteisesti väärin. Kysymyksen aihe valitaan käyttäjän syötteen perusteella. Vastaus on Moodlen Tentti-aktiviteetin XML-formaatin mukainen, tässä on esimerkki formaatista:

		        	<question type="multichoice">
					<name>
						<text>Kysymyksen nimi</text>
					</name>
					<questiontext format="html">
						<text>Kysymyksen teksti</text>
					</questiontext>
					<answer fraction="0">
		    			<text>Vastausvaihtoehto 1</text>
		   				<feedback><text>Väärin.</text></feedback>
					</answer>
					<answer fraction="0">
		    			<text>Vastausvaihtoehto 2</text>
		   				<feedback><text>Väärin.</text></feedback>
					</answer>
					<answer fraction="0">
						<text>Vastausvaihtoehto 3</text>
						<feedback><text>Melkein oikein.</text></feedback>
					</answer>
					<answer fraction="100">
		    			<text>Vastausvaihtoehto 4</text>
		   			<feedback><text>Oikein.</text></feedback>
					</answer>
					</question>
					"""
		        },
		        {"role": "system", "name": "example_assistant", "content": f"""
		        	Tässä on haluamasi monivalintakysymys:
		        	{sample_question}

		        	"""},
		        {"role": "system", "name":"user", "content": f"""Nyt, tulosta {iterations} kappaletta uniikkeja kysymyksiä tästä aiheesta: {topic}."""},
		    ],
		    temperature=0,
		    top_p=1,
		)
	except Exception as e:
		print("failed to generate for topic: " + topic)
		print(e)
		continue
	
	result = ''
	xml_cleaned = ''

	for choice in response.choices:
	    result += choice.message.content


	# create valid html
	
	for line in result.splitlines():
		if line.strip().startswith("<"):
			xml_cleaned += line + "\n"


	with filepath.open("a", encoding ="utf-8") as f:
		f.write(xml_cleaned)
		f.close()

# loop done, close xml

with filepath.open("a", encoding ="utf-8") as f:
    	f.write("</quiz>\n")
    	f.close()