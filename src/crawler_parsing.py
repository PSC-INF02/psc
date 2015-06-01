"""
@file crawler_parsing.py
@author PSC INF02

@brief Demos for crawler parsing.

We use the following methods :
@code
parse_for_systran("2015_03_29")
@endcode
Parsing of articles from our crawler,
suppressing a lot of tokenization errors.

@code
download_and_parse_data("2015_02_15")
@endcode
Downloading data for one day (useful in case
you want to reinitiate this data).

@code
update()
@endcode
Updates the crawler (may take a long time
if there is much data to parse).
"""

from abstracter.crawler.parse_crawler import update, parse_for_systran, download_and_parse_data


#################
# example 1
############

#parse_for_systran("2015_03_29")

##################
# example 2
###################

# download_and_parse_data("2015_02_15")

###################
# example 3
#########################

# update()
