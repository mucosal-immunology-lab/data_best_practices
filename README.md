# Data best practices

A guide to data storage best practices within the Mucosal Immunology Lab.

## Data storage and location

All raw sequening data and LCMS data needs to meet the following requirements:

### 1) Store data on the Vault

All data must be stored on the Monash Vault with minimal metadata (sample names, groups, library preparation kits, indexes etc.)

```bash
MONASH\\<MonashID>@vault-v2.erc.monash.edu:Marsland-CCS-RAW-Sequencing-Archive/vault/
```

#### Convert raw sequencing data

If your raw sequencing data is still in `BCL` format, following this [guide](https://github.com/mucosal-immunology-lab/microbiome-analysis/wiki/shotgun-preprocess) to convert data into FASTQ format.

#### Transfer your data to Vault

Transferring data is a simple process that involves using `rsync`, which is already installed on the M3 MASSIVE cluster. Simply swap out the following values:

* `local-folder-path`: the path to the local (or M3 MASSIVE cluster) folder.
* `MonashID`: your Monash ID.
* `sharename`: the name of the Vault share folder you want to copy to, i.e. `Marsland-CCS-RAW-Sequencing-Archive`.
* `path`: the path to the Vault folder.

```bash
rsync -aHWv --stats --progress --no-p --no-g --chmod=ugo=rwX /<local-folder-path>/ MONASH\\<MonashID>@vault-v2.erc.monash.edu:<sharename>/vault/<path>
```

#### Transfer your data from Vault

The same process works in reverse to retrieve data from the Vault.

```bash
rsync -aHWv --stats --progress --no-p --no-g --chmod=ugo=rwX MONASH\\<MonashID>@vault-v2.erc.monash.edu:<sharename>/vault/<path> /<local-folder-path>/
```

### 2) List dataset in the communal spreadsheet

The dataset must be listed in the Google Drive [**Sequencing Data**](https://docs.google.com/spreadsheets/d/1bKI-RgzfuWd-3C4_xZPCM-YlK7k0Fzn5/edit?usp=sharing&ouid=105349381251392029405&rtpof=true&sd=true) spreadsheet.

### 3) Be checked for integrity and quality

Be checked for data integrity (`md5 sum check`) and quality (`fastqc`).

#### MD5 sum check

*Script to be added.*

#### FastQC quality check

Prior to all pre-processing of sequencing data with their respective pipelines (e.g. dada2, Sunbeam, nf-core/rnaseq, or STARsolo), you must perform quality checks and read trimming to remove poor quality data.

For this purpose, we provide the following [`run_trimgalore.py`](./run_trimgalore.py) Python script. The script will run paired-end TrimGalore (and subsequent FastQC reporting) on each `fastq.gz` sample pair in a given folder and output the results to a selected folder.

First, create a new mamba environment (Python >= 3.5).

```bash
mamba create -n trimgalore -c bioconda python>=3.5 fastqc trim-galore
```

Then, run the script, providing at least the mandatory input and output directories. More options are specified below. Assuming you are working on the M3 MASSIVE cluster, first open a new interactive smux session, and then begin running the script (TrimGalore doesn't recommend any more than 8 cores for its parallel processing).

**Basic script**

```bash
python3 run_trimgalore.py -i raw_fastq -o QC --threads 8
```

You can also specify the following optional arguments:

* `length` (default: 40): the minimum length of paired-end reads in order to be kept.
* `quality` (default: 20): Phred score below which a read will be trimmed.

**Multi-threaded parallel script**

Alternatively, you can try the [multi-parallel script](./run_trimgalore_parallel.py) which will also run multiple samples in parallel while also providing multiple cores to each iteration of TrimGalore **(experimental)**. While you can provide a number of threads to the command line, the script will automatically determine the number of available threads, and use this value.

Further, it will try to divide the number of available cores between samples while providing at least 4 cores to any one sample for TrimGalore.

```bash
python3 run_trimgalore_parallel.py -i raw_fastq -o QC
```

*As mentioned, this is experimental, and sometimes seems to process only a single sample at a time despite having adequate cores to run multiple samples.*