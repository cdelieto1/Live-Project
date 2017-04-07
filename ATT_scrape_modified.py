#Python 2.7 written in PyCharm - Webscrape for ATT. 
from bs4 import BeautifulSoup
import requests
import os.path
import json

# Create a function to separate out data that is not a job posting.
def complete(dictionary):
    return(True) # TODO: Remove once testing is completed. It overrides the second return(True) during testing i.e. omits the Portland constraint. 
    if dictionary.get('Location') == 'Portland, Oregon':
        return(True)

# Establish raw data.
company = "ATT"
htmlFile = "temp/" + company + "html.txt"
baseurl = "https://connect.att.jobs"
url = baseurl + "/category/it-engineering-technology-jobs/117/29155/1"
jobs = []
other = []

# Establish link with web page to scrape and save html from
# web page to data and parse with BeautifulSoup.
'''
r = requests.get(url)
try:
    r.raise_for_status()
except Exception as exc:
    print('there was a problem: %s' % (exc))
data = r.text
soup = BeautifulSoup(data, "html.parser")
'''


##
# STEP 1: Get all/filtered job listings
#
# USE ATT ENDPOINT
#   This can be used to filter & to extract all postings programatically
#   through the returned HTML within the JSON.results key.
#
#   We set the resultsPerPage GET variable to some high number (I used 500. Sounds high enough to me) to get back
#   all job listings without the need to handle pagination in view.
#
#   JSON structure:
#     {
#        "filters":"<HTML>",
#        "results":"<HTML>" <-- this contains all job postings in HTML
#     }
##


url_get = "https://connect.att.jobs/search-jobs/results?ActiveFacetID=0&CurrentPage=1&RecordsPerPage=500&Distance=50&RadiusUnitType=0&Keywords=&Location=&Latitude=&Longitude=&ShowRadius=False&CustomFacetName=&FacetTerm=29155&FacetType=1&FacetFilters%5B0%5D.ID=29155&FacetFilters%5B0%5D.FacetType=1&FacetFilters%5B0%5D.Count=321&FacetFilters%5B0%5D.Display=IT+%5C+Engineering+%5C+Technology&FacetFilters%5B0%5D.IsApplied=true&FacetFilters%5B0%5D.FieldName=&SearchResultsModuleName=Search+Results&SearchFiltersModuleName=Search+Filters&SortCriteria=0&SortDirection=0&SearchType=2&CategoryFacetTerm=&CategoryFacetType=&LocationFacetTerm=&LocationFacetType=&KeywordType=&LocationType=&LocationPath=&OrganizationIds=117"
j = requests.get(url_get)
try:
    j.raise_for_status()
except Exception as e:
    print('there was a problem: %s' % (e))
#print j.text
jobs_all_json = json.loads(j.text)
#print jobs_all_json
#print jobs_all_json["results"]
jobs_all_html = jobs_all_json["results"]
soup = BeautifulSoup(jobs_all_html, "html.parser")

# STEP 2: extract job title, location & link
# Find all Divisions in the parsed website HTML with the class that contains
# the job data and divide all data into separate variables. Save all data to
# a dictionary named job in the format the Job Board App needs and run the function
# to separate real job data from all the other unwanted data unfortunately
# provided.

for links in soup.find_all('ul', class_="actual-results"):

    for link in links:

        jobTitle = None
        jobLocation = None
        applicationLink = None

        try:
            jobTitle = link.find_next('h2').contents[0].encode('utf-8').strip()
            print jobTitle
            jobLocation = link.find_next('span').contents[0]
            applicationLink = link.find_next('a').get('href')
            applicationLink = baseurl + applicationLink

            # STEP 3: extract job posting details from application link
            d = requests.get(applicationLink)
            descr = d.text
            soup = BeautifulSoup(descr, "html.parser")
            for descr in soup.find_all("div", class_="ats-description"):
                #print descr
                try:
                    applicationExperience = descr.find_next('ul').contents[0]
                    # print applicationExperience
                    print 'Got job description for: %s' % str(jobTitle)
                except Exception as e:
                    print 'Could not extract job descr for %s. Moving on...' % ( str(jobTitle) )

            job = {
                'ApplicationLink': applicationLink,
                'Company': company,
                'DatePosted': '',
                'Experience': '', #applicationExperience,
                'Hours': '',
                'JobID': '',
                'JobTitle': jobTitle,
                'LanguagesUsed': '',
                'Location': jobLocation,
                'Salary': '',
            }

            if complete(job):
                jobs.append(job)
                #print(job)
            else:
                other.append(job)

            print 'SUCCESS! Got all the info for %s \n' % jobTitle

        except Exception as e:
            print 'ERROR! Skipping job because of %s' % str(e)

with open(company + '.json', 'w') as outfile:
    json.dump(jobs, outfile)
