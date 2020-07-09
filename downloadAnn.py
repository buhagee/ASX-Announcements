from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from bs4 import BeautifulSoup
import lxml
import datetime
import requests
import sys
import os 

pdfPath = "announcement_files/pdfs/"

start_time = datetime.datetime.now()

today = str(datetime.date.today().strftime("%d-%m-%Y"))

# Checks command line arguments
if len(sys.argv) > 3: 
	print("Usage: python3 downAnn <'yesterday' or 'today'> <dd-mm-yyyy>")
	quit()
elif len(sys.argv) > 1:
	# Command line chooses whether to read today or yesterday's announcements
	if sys.argv[1] == "yesterday":
		# Yesterday announcements, changes date to previous trading day
		annPage = "https://www.asx.com.au/asx/statistics/prevBusDayAnns.do"
		today = datetime.date.today()-datetime.timedelta(days=1)
		while today.weekday() > 4:
			today -= datetime.timedelta(days=1)
		today = str(today.strftime("%d-%m-%Y"))
	elif sys.argv[1] == "today":
		# Todays announcements
		annPage = "https://www.asx.com.au/asx/statistics/todayAnns.do"
	else: 
		# Wrong usage
		print("Usage: python3 downAnn <yesterday/today> <dd-mm-yyyy>")
		quit()
	if len(sys.argv) > 2:
		# Manual date chosen
		today = sys.argv[2]
else:
	# defaults to todays announcements
	annPage = "https://www.asx.com.au/asx/statistics/todayAnns.do"


options = webdriver.ChromeOptions() # Doesn't visually open up chrome screen
options.add_argument("headless")

# Opens ASX announcements page
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.get(annPage)
content = driver.page_source
soup = BeautifulSoup(content, 'lxml')

# Picks table attribute
table = soup.find("table")
row = table.find_all('tr')

startUrl = "https://www.asx.com.au"


# Creates folder for todays announcements
if not os.path.exists(pdfPath+today):
    os.mkdir(pdfPath+today)

count = 0

for tr in row:

	# To skip heading
	check = tr.find('td')
	if not check:
		continue

	# Check if price sensitive
	check2 = tr.find('td', attrs={'class':'pricesens'})
	if not check2:
		continue
		
	# Company code
	code = check.get_text()

	# Time
	time = tr.find('span', attrs={'class':'dates-time'}).get_text()[0:-3]
	time = time[0:-3] + time[-2:]

	# Grabs middle link
	a = tr.find('a')
	tempLink = "".join((startUrl, a.get('href'))) 

	# Follows middle link
	tempDriver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
	tempDriver.get(tempLink)
	tempContent = tempDriver.page_source
	tempSoup = BeautifulSoup(tempContent, 'lxml')

	# Grabs announcement URL
	tempURL = tempSoup.find('input', attrs={'name':'pdfURL'}).get('value')

	tempDriver.close()

	# PDF URL
	url = "".join((startUrl, tempURL)) 

	# Save path
	path = pdfPath+today+'/'+code+'_'+time+'.pdf'

	# Accounts for multiple company announcements in day 
	i = 2
	while 1:
		newTime=time
		if os.path.isfile(path):
			newTime = time + '_' + str(i)
			path = pdfPath+today+'/'+code+'_'+newTime+'.pdf'
			i += 1
		else:
			time = newTime
			break

	# Downloads pdf to path
	r = requests.get(url)
	open(path, 'wb').write(r.content) 

	count += 1
	# Prints info to terminal
	print("\nAnnouncement: "+code+'_'+time+". Download number: "+str(count)+". Time elapsed: "+str(datetime.datetime.now() - start_time))

# Prints final info to terminal
elapsed_time = datetime.datetime.now() - start_time
print("\nDownloaded "+str(count)+" announcements to "+pdfPath+today+"'.\nTime elapsed: "+str(elapsed_time))

tempDriver.quit()
driver.quit()


