# Web Scraper for Ensembl Data Slicer

This tool utilizes Selenium to acess the [Ensembl Data Slicer Web Tool](https://www.ensembl.org/Homo_sapiens/Tools/DataSlicer?db=core;expand_form=true) through a Firefox webdriver.

## Installation

We provide a package file (``env.yml``) to create a new environment (``selenium_env``) using conda:

```bash
$ git clone https://github.com/smtnkc/ensembl-scraper.git
$ cd ensembl-scraper/
$ conda env create -f env.yml
$ conda activate selenium_env
```

:warning: Download [geckodriver](https://github.com/mozilla/geckodriver/releases) and put it in the same directory as this script.

## Arguments:
```bash
python runner.py \
        -o '<output_dir>' \
        -j '<job_name>' \
        -ff '<file_format>' \
        -r '<region_lookup>' \
        -g '<genotype_file_URL>' \
        -f '<filters>' \
        -m '<sample_population_mapping_file_URL>' \
        -p '<populations>' \
        -to '<timeout_in_seconds>'
```

You can also set ``--open`` to open Firefox Browser window.

## Sample Run Command:
```bash
python runner.py \
        -o 'downloads' \
        -j 'J2807' \
        -ff 'VCF' \
        -r '3:146142335-146301179' \
        -g 'https://ftp.ensembl.org/pub/data_files/homo_sapiens/GRCh38/variation_genotype/ALL.chr3_GRCh38.genotypes.20170504.vcf.gz' \
        -f 'populations' \
        -m 'https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/integrated_call_samples_v3.20130502.ALL.panel' \
        -p 'CEU' \
        -to '300'
```
