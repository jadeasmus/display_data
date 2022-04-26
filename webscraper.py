from flask import Flask, render_template, request, redirect, url_for
import numpy as np
from random import randint
import time
import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

app = Flask(__name__)


@app.route('/') # route decorator tells flask what url should trigger the function
def home(): # the function returns what we want displayed in user's browser
    return render_template("index.html")

# go to form where we get location for beautiful soup request
@app.route('/form', methods=['POST', 'GET'])
def get_data():
    if request.method == 'POST':
        location = request.form["nm"]
        print(f"lc is {location}")
        return redirect(url_for("scrape", lc=location))    
    else:
        print("I'm registering as GET")
        return render_template("form.html")



@app.route('/<lc>', methods=['POST', 'GET'])
def scrape(lc):
    print(f"location: {lc}")
    # replace spaces with dashes and lower case all
    lc = lc.lower()
    lc = lc.split(",")
    lc[0] = lc[0].replace(' ', '-') if ' ' in lc[0] else lc[0]
    

    # prep variables
    city, state = lc[0], lc[1]
    print(f"{state},{city}")
    # data to be collected
    names = []
    titles = []
    phone_numbers = []
    pt_links = []
    specialties = []
    picture = []
    insurances = []
    qualifications = []
    website = []
    bios = []

    pages = np.arange(1, 261, 20) # pages are split into 20 indiv results, allows for 14 pages of results
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }
    count = 1 # will keep track of results page number

    for page in pages:
        # timeout parameter to avoid getting ip address blocked
        page = requests.get(f"https://www.psychologytoday.com/us/therapists/{state}/{city}/?sid=6237a40de346c&rec_next="+str(page), headers=headers, timeout=(randint(2,10)))
        soup = BeautifulSoup(page.text, 'html.parser')
        therapist_div = soup.find_all('div', class_='results-row')
        # keep track of results progress, status code 200 means success
        print("Results page", count , page.status_code) 
        count += 1

        for container in therapist_div:
            # --names--
            name = container.find('a', attrs={'class': 'profile-title verified'}).text if container.find(attrs={'class': 'profile-title verified'}) else '-'
            names.append(name)
            # clean up results
            names = [l.replace('\n', '') for l in names] 

            # --licenses--
            title = container.find(attrs={'class': 'profile-subtitle'}).text if container.find(attrs={'class': 'profile-subtitle'}) else '-'
            titles.append(title)
            titles = [l.replace('\n ', ' ') for l in titles]

            # --phone numbers--
            phone = container.find(attrs={'class' : 'results-row-mob'}).text if container.find(attrs={'class' : 'results-row-mob'}) else '-'
            phone = phone.replace('\xa0', '').strip()
            phone_numbers.append(phone)

            # get indiv therapist profiles for additional info
            # get indiv therapist link
            headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
            }
            link = container.find('a').attrs['href']
            pt_links.append(link)
            req = requests.get(link, headers=headers, timeout=(randint(2,10)))
            s = BeautifulSoup(req.text, 'html.parser')

            # --specialties--
            specialty = s.find('ul', {'class': 'attribute-list specialties-list'}).text if s.find('ul', {'class': 'attribute-list specialties-list'}) else '-'
            specialties.append(specialty)
            specialties = [' '.join(e.split()) for e in specialties]

            # --insurances--
            ins = s.find(attrs={'class': 'col-split-xs-1 col-split-md-2'}).text if s.find(attrs={'class': 'col-split-xs-1 col-split-md-2'}) else '-'
            ins = ' '.join(ins.split())
            insurances.append(ins)

            # --qualifications--
            q = s.find(attrs={'class': 'profile-qualifications details-section top-border'}) if s.find(attrs={'class': 'profile-qualifications details-section top-border'}) else '-'
            if q != '-':
                qualifications.append(q.li.text.replace('\n', ''))
            else:
                qualifications.append(q)
            qualifications = [' '.join(q.split()) for q in qualifications] # clean up spacing

            # --website--
            site = s.find('a', {'class': 'btn btn-md btn-profile btn-default hidden-sm-down'}) if s.find('a', {'class': 'btn btn-md btn-profile btn-default hidden-sm-down'}) else '-'
            if site != '-':
                website.append(site['href'])
            else:
                website.append(site)

            # --bio--
            full=[]
            bio = s.find_all('div', {'class': 'statementPara'}) if s.find_all('div', {'class': 'statementPara'}) else '-'
            if bio != '-':
                for b in bio:
                    full.append(b.text)
            else:
                bios.append(bio)
            bios.append(full)


    
    return render_template('results.html', names=names, titles=titles, phone_numbers=phone_numbers, specialties=specialties, insurances=insurances, qualifications=qualifications, website=website, bios=bios) if names else "there was a problem"



if __name__ == '__main__':
    app.run(debug=True)