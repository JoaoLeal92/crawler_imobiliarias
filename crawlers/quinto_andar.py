import requests
import argparse
import json
import smtplib
from email.message import EmailMessage
from datetime import datetime
from unidecode import unidecode

from utils import parse_city, IncorrectArgsException
from crawler_settings import QUINTO_ANDAR_REGION_SETTINGS, QUINTO_ANDAR_URL, EMAIL_ORIGIN, EMAIL_DESTINATION, PASSWORD

# User input variables
parser = argparse.ArgumentParser(description='Crawler for Quinto Andar website (www.quintoandar.com.br)')
parser.add_argument('-s', '--state', type=str,
                    help='Abbreviated name of state to search for real estates (ex.: SP, RJ, etc.)')
parser.add_argument('-c', '--city', type=str, help='city to search for real estates')
parser.add_argument('-b', '--bedrooms', nargs='*', type=int, help='Total number of bedrooms in the estate')
parser.add_argument('-max', '--maxArea', type=int, help='Maximum area of the estate')
parser.add_argument('-min', '--minArea', type=int, help='Minimum area of the estate')
parser.add_argument('-maP', '--maxPrice', type=float, help='Minimum price of the estate')
parser.add_argument('-miP', '--minPrice', type=float, help='Minimum price of the estate')
parser.add_argument('-g', '--garageSpots', nargs='*', type=int, help='Number of available garage spots the estate')
parser.add_argument('-r', '--region', nargs='*', type=str, help='Number of available garage spots the estate')
args = parser.parse_args()

if len(args.state) > 2:
    raise IncorrectArgsException('State must be in abbreviated form')

# Parse the city and state names
parsed_city = parse_city(args.city)
upper_case_state = args.state.upper()
lower_case_state = args.state.lower()

# Get the boudaries params for the desired city (must be previously mapped and added to the settings file)
city_params = QUINTO_ANDAR_REGION_SETTINGS.get(parsed_city)

# Request headers
headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
    'content-type': 'application/json'
}

# Form data to be sent on the request
form_data = {
    "business_context": "sale",
    "context": {
        "dt": datetime.now().isoformat(),
        "map": city_params,
        "search_dropdown_value": f"{args.city}, {upper_case_state}, Brasil",
        "search_filter": {
            "area_max": 1000,
            "area_max_changed": False,
            "area_min": 20,
            "area_min_changed": False,
            "price_max": 20000,
            "price_max_changed": False,
            "price_min": 500,
            "price_min_changed": False,
            "price_type": "rent"
        },
    },
    "criteria": {
        "expr.distance": f"floor(haversin({city_params['center_lat']}%2C{city_params['center_lng']}%2Clocal.latitude%2Clocal.longitude)*1000*0.002)",
        "expr.rank": "((-10*distance%2Brelevance_score)*(0.1))",
        "fq": f"local:['{city_params['bounds_north']},{city_params['bounds_west']}','{city_params['bounds_south']},{city_params['bounds_east']}']",
        "q": "for_sale:'true'",
        "q.parser": "structured",
        "return": "id,foto_capa,aluguel,area,quartos,custo,photos,photo_titles,endereco,regiao_nome,cidade,visit_status,special_conditions,listing_tags,tipo,promotions,for_rent,for_sale,sale_price,condo_iptu,vagas",
        "size": 10000,
        "sort": "rank desc",
        "start": 0
    },
    "user_id": "13cf3601-99bc-4525-908d-d9e5137ca134R"
}

json_data = json.dumps(form_data)

# Make the get request and convert json response to dict
response = requests.post(QUINTO_ANDAR_URL, data=json_data, headers=headers)
response_content = json.loads(response.text)
if 'hits' in response_content:
    available_estates = response_content['hits']['hit']
    # Creates a local copy of available estates to be filtered
    filtered_estates = available_estates.copy()
else:
    raise Exception('There was an error in your request, check the arguments passed')

# Applying filters
if args.bedrooms:
    filtered_estates = [estate for estate in filtered_estates if int(estate['fields']['quartos']) in args.bedrooms]
if args.maxArea:
    filtered_estates = [estate for estate in filtered_estates if int(estate['fields']['area']) < args.maxArea]
if args.minArea:
    filtered_estates = [estate for estate in filtered_estates if int(estate['fields']['area']) > args.minArea]
if args.maxPrice:
    filtered_estates = [estate for estate in filtered_estates if int(estate['fields']['sale_price']) < args.maxPrice]
if args.minPrice:
    filtered_estates = [estate for estate in filtered_estates if int(estate['fields']['sale_price']) > args.minPrice]
if args.garageSpots:
    filtered_estates = [estate for estate in filtered_estates if int(estate['fields']['vagas']) in args.garageSpots]
if args.region:
    parsed_regions = [unidecode(region.lower()) for region in args.region]
    filtered_estates = [estate for estate in filtered_estates if unidecode(estate['fields']['regiao_nome'].lower()) in parsed_regions]

# Generate the links to access the page of each estate offer
links = []
for estate in filtered_estates:
    estate_link = f'https://www.quintoandar.com.br/imovel/{estate["id"]}/comprar'
    links.append(estate_link)

# Sends e-mail with the links
email_content = 'Resultados da pesquisa\n'

for link in links:
    email_content += link + '\n'

msg = EmailMessage()
msg.set_content(email_content)
msg['Subject'] = 'Apartamentos à venda'
msg['From'] = EMAIL_ORIGIN
msg['To'] = EMAIL_DESTINATION

# create server
server = smtplib.SMTP('smtp.gmail.com: 587')

server.starttls()

# Login Credentials for sending the mail
server.login(msg['From'], PASSWORD)

# send the message via the server.
server.sendmail(msg['From'], msg['To'], msg.as_string())

server.quit()

print('Mensagem enviada com sucesso')