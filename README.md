# PIIFinder
Python application using spaCy to find Personal Identifying Information in any text file.

## Installation  
1. The first step is to install Python 3.7 or higher, if you don't already have it on your system. This will may be slightly different on Windows, MacOS and Linux. 
    https://www.python.org/downloads/

    If you're behind a corporate firewall you might need to use the second set of commands to complete the download. 
1. Then install **spaCy** using pip. For more information regarding spaCy: https://spacy.io/
    ```
    pip install spaCy
    or
    pip --cert [ca-bundle cert] --proxy [proxy address:port] install spacy
    ```
3. Download the **Pre-Trained Model**. spaCy offers 3 different models, we're using the large version. For more info regarding spaCy's models: https://spacy.io/models/en 
    ```
    python -m spacy download en_core_web_lg
    or
    pip --cert [ca-bundle cert] --proxy [proxy address:port] install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-2.2.5/en_core_web_lg-2.2.5.tar.gz
    ```
    ### Manual Model install
    If you run into issues downloading the pre-trained model using pip, you can   download the model manually using this link: https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.0.0/en_core_web_lg-3.0.0.tar.gz
    Then run pip against the local file to install it.

    ```
    pip install path/to/model/en_core_web_lg-3.0.0.tar.gz
    ```
1. Next, either clone or download the **PIIFinder**  code from github.
    ```
    git clone https://github.com/SanDiegoCountySheriff/PIIFinder.git
    or
    Download the files directly from github, then extract them from the ZIP file.
    ```

## How to use the PIIFinder: Instructions

1. Open the folder (PIIFinder-master) where you saved the files from git 
1. Double click FinderTrainer.py
1. Click on the "Select Files" button and select the files you'd like to scan for PII. Any text file will work.
1. Click on the "Scan" button
1. After the scan is done review the results. To exclude words in future runs, click the button of the words. This will help prevent false positive matching on specific words.

    * When you click on the button, the word in the button is added to the AmbiguousNames.txt file. This file includes words that aren't included in the results.
    * After the scan is finished 3 logs appear inside of the Result_Logs directory
        * NAMES [Date/Time][File Scanned Name].txt
        * REGEX [Date/Time][File Scanned Name].txt
        * TIME  [Date/Time][File Scanned Name].txt
    
The NAMES file will contain all the lines with PII found by the program.  
The REGEX file contains the lines containing strings that match the regular expression defined in PIIFinder/Wordlists/REGEX.txt.  
The TIME file contains the time it took to complete the scan.  

## Customizing Your Scan
The Wordlists directory comes with 3 files.
* NAMES.txt
* REGEX.txt
* AmbiguousNames.txt

Customize the NAMES.txt file to add or remove names to look for.  
Customize the REGEX.txt file to add or remove regex patterns for the program to find.  
Customize the AmbiguousNames.txt file to tell the program what names to filter out of the results.  
(Names are added automatically to the AmbiguousNames.txt file when clicking the buttons within the results list of the GUI)
