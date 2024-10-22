from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
import gzip
import os
import time
import re

def setup_driver():
    # Set up the Selenium WebDriver for Firefox
    options = Options()
    # options.add_argument('-headless')  # Run in headless mode
    return webdriver.Firefox(options=options)

def create_download_folder():
    # Create a folder to store downloaded files
    folder_name = "tcga_gene_expression_data"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def get_tcga_cohorts(driver):
    # Navigate to the TCGA hub page
    driver.get("https://xenabrowser.net/datapages/?host=https://tcga.xenahubs.net")
    time.sleep(2)   # Wait for the web page to load

    # Wait for the cohorts to load
    wait = WebDriverWait(driver, 20)
    
    # First, wait for the list to be present
    list_selector = "ul.Datapages-module__list___2yM9o"
    list_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, list_selector)))
    
    # Then, find all 'a' elements within this list
    link_elements = list_element.find_elements(By.TAG_NAME, "a")
    
    print([link.text for link in link_elements if link.text])
    
    # Extract text from each link
    return [link.text for link in link_elements if link.text]  # Only include non-empty texts

def download_gene_expression_data(driver, cohort, download_folder):
    # Navigate to the cohort page
    driver.get(f"https://xenabrowser.net/datapages/?cohort={cohort}&removeHub=https%3A%2F%2Fxena.treehouse.gi.ucsc.edu%3A443")

    # Wait for the IlluminaHiSeq page to load
    wait = WebDriverWait(driver, 10)
    try:
        illuminahiseq_page_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'IlluminaHiSeq pancan normalized')]")))
    except TimeoutException:
        print(f"No gene expression IlluminaHiSeq found for {cohort}")
        return

    # Get the IlluminaHiSeq page link
    illuminahiseq_page_url = illuminahiseq_page_link.get_attribute('href')


    driver.get(illuminahiseq_page_url)
    time.sleep(2)   # Wait for the web page to load

    # Find the download row
    wait = WebDriverWait(driver, 10)
    try:
        download_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[starts-with(@href, 'https://tcga-xena-hub.s3.us-east-1.amazonaws.com/download/') and contains(@href, '.gz')]")))
    except TimeoutException:
        print(f"No gene expression download link found for {cohort}")
        return


    # Extract the download link
    download_url = download_link.get_attribute('href')
    
    if download_url:
        
        response = requests.get(download_url)
        if response.status_code == 200:
            compressed_filename = os.path.join(download_folder, f"{cohort}.gz")
            with open(compressed_filename, 'wb') as f:
                f.write(response.content)
            
            decompressed_filename = os.path.join(download_folder, f"{cohort}.tsv")
            with gzip.open(compressed_filename, 'rb') as f_in:
                with open(decompressed_filename, 'wb') as f_out:
                    f_out.write(f_in.read())
            
            os.remove(compressed_filename)
            
            print(f"Downloaded and decompressed data for {cohort}")
        else:
            print(f"Failed to download data for {cohort}")
    else:
        print(f"No download link found for {cohort}")

def main():
    driver = setup_driver()
    download_folder = create_download_folder()
    try:
        cohorts = get_tcga_cohorts(driver)
        for cohort in cohorts:
            download_gene_expression_data(driver, cohort, download_folder)
            time.sleep(2)  # Add a small delay between requests to be polite to the server
    finally:
        driver.quit()

if __name__ == "__main__":
    main()