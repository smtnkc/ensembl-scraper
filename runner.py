#!/usr/bin/env python3

__author__ = "Samet Tenekeci"
__license__ = "MIT"
__version__ = "03.08.2023"
__email__ = "samettenekeci@iyte.edu.tr"

import os
import time
import sys
import argparse as ap
import logging
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

def parse_params():
    p = ap.ArgumentParser(prog='ensembl_data_slicer.py',
                          description="Get a subset of data from a BAM or VCF file.")

    p.add_argument('-i', '--inputcsv',
                metavar='[STR]', type=str, required=False, default='inputs.csv',
                help="Input CSV file")

    p.add_argument('-o', '--outdir',
                   metavar='[STR]', type=str, required=False, default='downloads/',
                   help="Output directory")

    p.add_argument('-j', '--jobname',
                   metavar='[STR]', type=str, required=False, default=None,
                   help="Name for this job")

    p.add_argument('-ff', '--fileformat',
                   metavar='[STR]', type=str, required=False, default='VCF',
                   help="File format (BAM or VCF)")

    p.add_argument('-r', '--regionlookup',
                   metavar='[STR]', type=str, required=False, default='3:146142335-146301179',
                   help="Region Lookup")

    p.add_argument('-g', '--genotype',
                   metavar='[STR]', type=str, required=False,
                   default='https://ftp.ensembl.org/pub/data_files/homo_sapiens/GRCh38/variation_genotype/ALL.chr3_GRCh38.genotypes.20170504.vcf.gz',
                   help="Genotype file URL")

    p.add_argument('-f', '--filters',
                   metavar='[STR]', type=str, required=False, default='populations',
                   help="Filters (null, individuals, or populations)")

    p.add_argument('-m', '--mapping',
                   metavar='[STR]', type=str, required=False,
                   default='https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/integrated_call_samples_v3.20130502.ALL.panel',
                   help="Sample-population mapping file URL")

    p.add_argument('-p', '--populations',
                   metavar='[STR]', type=str, required=False, default='CEU',
                   help="Populations")

    p.add_argument('--open',
                   action='store_true',
                   help='Open Firefox browser window.')

    p.add_argument('-to', '--timeout',
                   metavar='[INT]', type=int, required=False, default=300,
                   help="Set action timeout seconds. Default is 300 secs.")

    args_parsed = p.parse_args()
    if not os.path.exists(args_parsed.outdir):
        os.makedirs(args_parsed.outdir)
    return args_parsed


def waiting_sys_timer(wait, sec=1):
    """wait for system timer"""
    try:
        wait.until(EC.invisibility_of_element_located(
            (By.XPATH, "//div[@class='overlay-spinner spinner']")))
    except:
        pass

    time.sleep(sec)


def waiting_results(wait, sec=1):
    """wait for system timer"""
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='[View results]']")))
    except:
        pass

    time.sleep(sec)


def download_ensembl_data(
        o,      # output directory
        j,      # job name
        ff,     # file format
        r,      # region lookup
        g,      # genotype file URL
        f,      # filters
        m,      # sample-population mapping file URL
        p,      # populations
        to,     # timeout in seconds
        open    # open browser
    ):

    # all arguments required
    if not (o and j and ff and r and g and f and m and p, to, open):
        logging.error("Missing argument.")
        sys.exit(1)

    if j[0] != 'J':
        logging.error("Job name must start with 'J'.")
        sys.exit(1)

    # output directory
    if not os.path.exists(o):
        os.makedirs(o, exist_ok=True)

    o = os.path.abspath(o)

    # MIME types
    mime_types = "application/octet-stream"
    mime_types += ",application/excel,application/vnd.ms-excel"
    mime_types += ",application/pdf,application/x-pdf"
    mime_types += ",application/x-bzip2"
    mime_types += ",application/x-gzip,application/gzip"

    logging.info("Opening browser...")

    options=Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", o)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", mime_types)
    options.set_preference("plugin.disable_full_page_plugin_for_types", mime_types)
    options.set_preference("pdfjs.disabled", True)

    if not open:
        options.add_argument('-headless')

    service = Service(r'./geckodriver')
    # Download geckodriver from https://github.com/mozilla/geckodriver/releases and
    # put it in the same directory as this script
    driver = webdriver.Firefox(service=service, options=options)

    # driverwait
    driver.implicitly_wait(0)
    wait = WebDriverWait(driver, to)

    # open ENSEMBL
    logging.info("Opening website ensembl data slicer...")
    driver.get('https://www.ensembl.org/Homo_sapiens/Tools/DataSlicer?db=core;expand_form=true')
    waiting_sys_timer(wait)
    logging.info(driver.title)

    logging.info("Closing agreement...")
    results_button = driver.find_element(By.XPATH, "//a[@id='gdpr-agree']")
    results_button.click()
    waiting_sys_timer(wait)

    logging.info("Setting job name...")
    j_input = driver.find_element(By.XPATH, "//input[@name='name']")
    j_input.send_keys(j)
    waiting_sys_timer(wait)

    logging.info("Setting file format...")
    ff_input = driver.find_element(By.XPATH, "//select[@name='file_format']")
    ff_select = Select(ff_input)
    ff_select.select_by_visible_text(ff)
    waiting_sys_timer(wait)

    logging.info("Setting region lookup...")
    r_input = driver.find_element(By.XPATH, "//input[@name='region']")
    r_input.send_keys(r)
    waiting_sys_timer(wait)

    logging.info("Setting genotype file URL...")
    g_input = driver.find_element(By.XPATH, "//input[@name='custom_file_url']")
    g_input.send_keys(g)
    waiting_sys_timer(wait)

    logging.info("Setting filters...")
    f_radio = driver.find_element(By.XPATH, '//input[@value="{}"]'.format(f))
    f_radio.click()
    waiting_sys_timer(wait)

    logging.info("Setting sample-population mapping file URL...")
    m_input = driver.find_element(By.XPATH, "//input[@name='custom_sample_url']")
    m_input.send_keys(m)
    waiting_sys_timer(wait)

    banner_element = driver.find_element(By.XPATH, "//div[@id='masthead']")
    banner_element.click()
    waiting_sys_timer(wait)

    logging.info("Setting population...")
    p_input = driver.find_element(By.XPATH, "//select[@name='custom_populations']")
    p_select = Select(p_input)
    p_select.select_by_visible_text(p)
    waiting_sys_timer(wait)

    logging.info("Running...")
    run_button = driver.find_element(By.XPATH, "//input[contains(@class, 'run_button')]")
    run_button.click()
    waiting_sys_timer(wait)

    logging.info("Waiting for the results (In the queue)...")
    waiting_results(wait)
    logging.info("Results are ready...")
    results_button = driver.find_element(By.XPATH, "//a[text()='[View results]']")
    results_button.click()
    waiting_sys_timer(wait)

    logging.info("Downloading results...")
    results_button = driver.find_element(By.XPATH, "//a[text()='Download results file']")
    results_button.click()
    waiting_sys_timer(wait)

    # close driver
    driver.quit()


def get_last_downloaded_file(directory):
    # Get a list of all files in the directory along with their modification times
    files = [(filename, os.path.getmtime(os.path.join(directory, filename))) for filename in os.listdir(directory)]

    # Sort the files based on their modification times (most recent first)
    files.sort(key=lambda x: x[1], reverse=True)

    # Return the name of the most recently modified file (the last one in the sorted list)
    return files[0][0] if files else None


def rename_file(directory, last_downloaded_file, new_name):
    old_file_path = os.path.join(directory, last_downloaded_file)
    new_file_path = os.path.join(directory, new_name)
    os.rename(old_file_path, new_file_path)


def main():
    argvs = parse_params()

    logging.info(f"ENSEMBL Data Slicer V{__version__}")

    if argvs.inputcsv:
        logging.info("Reading input CSV file...")

        with open(argvs.inputcsv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                download_ensembl_data(
                    argvs.outdir,
                    row['jobname'],
                    row['fileformat'],
                    row['regionlookup'],
                    row['genotype'],
                    row['filters'],
                    row['mapping'],
                    row['populations'],
                    argvs.timeout,
                    open=False
                )
                logging.info("Renaming the last downloaded file...")
                last_downloaded_file = get_last_downloaded_file(argvs.outdir)
                rename_file(argvs.outdir, last_downloaded_file, row['jobname'] + '.vcf.gz')
                print('*' * 50)

    else:
        download_ensembl_data(
            argvs.outdir,
            argvs.jobname,
            argvs.fileformat,
            argvs.regionlookup,
            argvs.genotype,
            argvs.filters,
            argvs.mapping,
            argvs.populations,
            argvs.timeout,
            argvs.open
        )
        logging.info("Renaming file...")
        matching_files = get_last_downloaded_file(argvs.outdir)
        rename_file(argvs.outdir, matching_files, argvs.jobname + '.vcf.gz')

    logging.info("Completed.")

if __name__ == "__main__":
    main()
