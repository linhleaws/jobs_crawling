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
            No jobs were found for the given search criteria.
            Please consider the following:
            1. Try adjusting your search criteria.
            2. If you used English search keywords for non-English speaking countries,
               it might return an empty result. Consider using keywords in the country's language.
            3. Try more general keyword(s), check your spelling or replace abbreviations with the entire word

            Feel free to try a manual search with this link and see for yourself:
            Link {full_url}
            """
            send_message_slack(message)

            # subject = 'No Jobs Found on Indeed'
            # body = """
            # No jobs were found for the given search criteria.
            # Please consider the following:
            # 1. Try adjusting your search criteria.
            # 2. If you used English search keywords for non-English speaking countries,
            #    it might return an empty result. Consider using keywords in the country's language.
            # 3. Try more general keyword(s), check your spelling or replace abbreviations with the entire word

            # Feel free to try a manual search with this link and see for yourself:
            # Link {}
            # """.format(full_url)

            # send_email_empty(sender_email, receiver_email, subject, body, password)
            print(df)
        else:
            cleaned_df = clean_data(df)
            # csv_file = save_csv(cleaned_df, job_position, job_location)
    finally:
        try:
            # send_email(cleaned_df, sender_email, receiver_email, job_position, job_location, password)
            write_to_s3(cleaned_df, job_position, job_location)
        except Exception as e:
            message = f"Error saving file: {e}"
            send_message_slack(message)
        finally:
            pass
            driver.quit()


if __name__ == "__main__":
    main()