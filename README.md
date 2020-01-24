# PIIFinder
Python Application using spaCy to find PII

## Requirements  
##### If you're behind a corporate firewall you might need to use the second set of commands to complete the download.
**PIIFinder**  
```
git clone https://github.com/SanDiegoCountySheriff/PIIFinder.git
or
Download the files directly
```
**spaCy**  
```
pip install spaCy
or
pip --cert [ca-bundle cert] --proxy [proxy address:port] install spacy
```
**Pre-Trained Model**  
spaCy offers 3 different models. In the example we're using the large version.  
For more info regarding spaCy's models: https://spacy.io/models/en 
```
python -m spacy download en_core_web_lg
or
pip --cert [ca-bundle cert] --proxy [proxy address:port] install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-2.2.5/en_core_web_lg-2.2.5.tar.gz
```

## Instructions
1. Click on the "Select Files" button and select the files you'd like to scan for PII.
1. Click on the "Scan" button
1. After the scan is done look through the results and click on the buttons that include words that you wouldn't like to search for again.
    * When you click on the button, the word in the button is added to the AmbiguousNames.txt file. This file includes words that aren't included in the results.

* After the scan is finished a 3 logs appear inside of the Result_Logs directory
    * NAMES [Date/Time][File Scanned Name].txt
    * REGEX [Date/Time][File Scanned Name].txt
    * TIME  [Date/Time][File Scanned Name].txt
    
The NAMES file will contain all the lines with PII found by the program.  
The REGEX file contains the lines containing strings that match the regular expression.  
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
