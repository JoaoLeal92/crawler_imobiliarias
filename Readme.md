# Web Crawler for real estate websites

This crawler aims to get price data from real estates searching each of the websites contained in the "crawlers" directory
Links for each estate found will be sent via e-mail

## Install dependencies (using Anacnoda)
conda env create -f env.yml

## Activate conda environment
conda activate crawler_imobiliarias

## Set operation parameters
In the crawlers/crawler_settings.py file, set the following parameters:
    EMAIL_ORIGIN = email from which the message will be sent
    PASSWORD = password to access e-mail account
    EMAIL_DESTINATION = destination to which the message will be sent
   
## Get help for crawler operation parameters
python path/to/quinto_andar.py --help

## Run crawler (Example using only city and state params)
python path/to/quinto_andar.py -c "São Paulo" -s SP
