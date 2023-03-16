import sys
import openai
from pathlib import Path
import traceback
import logging
import argparse

parser = argparse.ArgumentParser(description='Creates SBA questions in Moodle Quiz XML format from a topic list, using the ChatGPT API.')
parser.add_argument('topicfile', type=str, metavar='topicfile',
                    help='Name of the topic file containing one topic per line')
parser.add_argument('iterations', type=int, metavar='iterations',
                    help='How many questions per topic should be created')
parser.add_argument('outputfile', type=str, metavar='outputfile',
                    help='Name of the file where the questions should be saved')
parser.add_argument('--debug', help='output everything on stdout')
parser.add_argument('--samplequestion', type=str, metavar='filename', help='This file specifies a sample question that helps to prime the language model. If there is not one, the default sample question is used instead.')
args = parser.parse_args()


# PARAMETERS: 1. topic file (list of question topics separated by newline) 2. Number of questions per topic 3. name of output xml file
# Additionally, sample_question.txt for a question to prime the gpt api. If the file doesn't exist, the default sample question is used instead.

topicfile = args.topicfile
openai.api_key = "API KEY HERE"

topics = Path(topicfile).read_text()
topics_list = topics.split("\n")
xml_header = '<?xml version="1.0"?>\n<quiz>\n'

iterations = args.iterations

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

if args.samplequestion:
	sample_question_file = Path(args.samplequestion)
	if sample_question_file.is_file():
		sample_question = Path(sample_question_file).read_text()
		print("Custom sample question file found, using it to generate questions.")
	else:
		print("Sample question file not found. Using the default sample question")
else:
    print("Sample question file not found. Using the default sample question")

filepath = Path(args.outputfile)
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
		        {"role": "system", "name":"example_user", "content": f"""Haluan, että tulostat {iterations} erillistä monivalintakysymystä, joissa on neljä vaihtoehtoista vastausta. Neljäs vastaus on oikea vastaus. Kolmas vastaus on lähellä oikeaa vastausta, mutta silti yksiselitteisesti väärin. Kysymyksen aihe valitaan käyttäjän syötteen perusteella. Kysymysten tulee olla Bloomin taksonomian kolmannella tai korkeammalla tasolla. Kysymysten pitää siis vaatia tiedon soveltamista tai analysointia, eikä vain muistamista ja ymmärtämistä. Kysymysten tulisi olla sellaisia, että vastaus ei löydy suoraan hakukoneella. Vastaus on Moodlen Tentti-aktiviteetin XML-formaatin mukainen, tässä on esimerkki formaatista:

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
