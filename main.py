import os
from job_scraper_utils import *
from dotenv import load_dotenv
import boto3

load_dotenv()

def main():
    driver = configure_webdriver()
    country = os.getenv("VIETNAM")
    job_position = 'data engineer'
    job_location = 'ho chi minh city'
    date_posted = 0 # crawling for the past 30 days

    cleaned_df = None

    try:
        full_url = search_jobs(driver, country, job_position, job_location, date_posted)
        df = scrape_job_data(driver, country)
        # incase of no results
        if df.shape[0] == 1:
            message = f"""
            No results found. Something went wrong.
            Check the URL: {full_url}
            """
            send_message_slack(message)
        else:
            cleaned_df = clean_data(df)
    finally:
        try:
            write_to_s3(cleaned_df, job_position, job_location)
        except Exception as e:
            message = f"Error saving file: {e}"
            send_message_slack(message)
        finally:
            pass
            driver.quit()


if __name__ == "__main__":
    main()