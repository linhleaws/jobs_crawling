import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc #bypass Cloudflare

global total_jobs


def configure_webdriver():
    '''Connfigure the Chrome webdriver like a person'''
    # options = webdriver.ChromeOptions()
    options = uc.ChromeOptions() # test with library bypass Cloudflare
    # options.add_argument("--headless")
    # options.add_argument("start-maximized")
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver = uc.Chrome(options=options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    return driver


def search_jobs(driver, country, job_position, job_location, date_posted):
    '''Count how many jobs are available for the given search criteria'''
    full_url = f'{country}/jobs?q={"+".join(job_position.split())}&l={"+".join(job_location.split())}&fromage={date_posted}'
    # full_url = f'{country}/jobs?q={"+".join(job_position.split())}&l={job_location}&fromage={date_posted}'

    # print(full_url)
    driver.get(full_url)
    time.sleep(5)
    global total_jobs
    try:
        # find element with class name start with 'jobsearch-JobCountAndSortPane-jobCount'
        job_count_element = driver.find_element(By.XPATH,
                                                '//div[starts-with(@class, "jobsearch-JobCountAndSortPane-jobCount")]')
        total_jobs = job_count_element.find_element(By.XPATH, './span').text
        # message = f"{total_jobs} found"
        print(f"{total_jobs} found")
    except NoSuchElementException:
        print("No job count found")
        total_jobs = "Unknown"

    # driver.save_screenshot('screenshot.png')
    return full_url


def scrape_job_data(driver, country):
    '''Scrape the job data from the page'''
    df = pd.DataFrame({'job_id': [''], 'link': [''], 'job_title': [''], 'company': [''],
                       'employer_active': [''], 'location': ['']})
    job_count = 0
    # count = 0
    while True:
        # count += 1
        soup = BeautifulSoup(driver.page_source, 'lxml')

        boxes = soup.find_all('div', class_='job_seen_beacon')
        for i in boxes:
            try:
                # check a tag with data-jk attribute
                job_id = i.find('a', {'data-jk': True}).get('data-jk')
                link = i.find('a', {'data-jk': True}).get('href')
                link_full = country + link
            except (AttributeError, TypeError):
                try:
                    job_id = i.find('a', class_=lambda x: x and 'JobTitle' in x).get('data-jk')
                    link = i.find('a', class_=lambda x: x and 'JobTitle' in x).get('href')
                    link_full = country + link
                except (AttributeError, TypeError):
                    job_id = None
                    link_full = None

            try:
                job_title = i.find('a', class_=lambda x: x and 'JobTitle' in x).text.strip()
            except AttributeError:
                try:
                    job_title = i.find('span', id=lambda x: x and 'jobTitle-' in str(x)).text.strip()
                except AttributeError:
                    job_title = None

            try:
                company = i.find('span', {'data-testid': 'company-name'}).text.strip()
            except AttributeError:
                try:
                    company = i.find('span', class_=lambda x: x and 'company' in str(x).lower()).text.strip()
                except AttributeError:
                    company = None

            try:
                employer_active = i.find('span', class_='date').text.strip()
            except AttributeError:
                try:
                    employer_active = i.find('span', {'data-testid': 'myJobsStateDate'}).text.strip()
                except AttributeError:
                    employer_active = None

            try:
                location_element = i.find('div', {'data-testid': 'text-location'})
                if location_element:
                    try:
                        location = location_element.find('span').text.strip()
                    except AttributeError:
                        location = location_element.text.strip()
                else:
                    raise AttributeError
            except AttributeError:
                try:
                    location_element = i.find('div', class_=lambda x: x and 'location' in str(x).lower())
                    if location_element:
                        try:
                            location = location_element.find('span').text.strip()
                        except AttributeError:
                            location = location_element.text.strip()
                    else:
                        location = ''
                except AttributeError:
                    location = ''

            new_data = pd.DataFrame({'job_id': [job_id], 'link': [link_full], 'job_title': [job_title],
                                     'company': [company],
                                     'employer_active': [employer_active],
                                     'location': [location]})

            df = pd.concat([df, new_data], ignore_index=True)
            job_count += 1

        print(f"Scraped {job_count} of {total_jobs}")

        try:
            next_page = soup.find('a', {'aria-label': 'Next Page'}).get('href')

            next_page = country + next_page
            driver.get(next_page)

        except:
            break

    return df


def clean_data(df):
    def posted(x):
        try:
            x = x.replace('EmployerActive', '').strip()
            return x
        except AttributeError:
            pass
    df['employer_active'] = df['employer_active'].apply(posted)
    return df