from tkinter.filedialog import askopenfilenames
from itertools import product
from tkinter import ttk
import multiprocessing
import tkinter as tk
import datetime
import os.path
import spacy
import time
import sys
import re
import os
import io

####################
# Global Variables #
####################
deletion_list = []
path_list     = ""
exp_list      = ""
first_char    = ""
# EDIT AS NEEDED #
AMBIG_PATH = 'Wordlists/AmbiguousNames.txt'
WORDLIST   = 'Wordlists/NAMES.txt'
REGEX_PATH = 'Wordlists/REGEX.txt'

#############
# Functions #
#############

# hide_me: Removes label that was clicked from list of results and
#          adds the name that was found on label to AmbiguousNames.txt     
def hide_me(event):

    list_in_row = scrollable_frame.grid_slaves(row=int(event.widget.grid_info()['row']))
    for i in list_in_row:
        i.grid_forget()

    to_delete = event.widget.cget('text')

    # Appends entries from deletion_list to AmbiguousNames.txt
    with open(AMBIG_PATH, 'a') as f:
        f.write("%s\n" % to_delete)

    uniqlines = set(open(AMBIG_PATH).readlines())
    uniqlines = list(uniqlines)
    uniqlines.sort()
    bar = open(AMBIG_PATH, 'w')
    bar.writelines(uniqlines)
    bar.close()
    
# progressbar: Displays a progress bar to console
def progressbar(progress, total, printEnd = "\r"):

    percent = "{0:.2f}".format(round(((progress/total) * 100),1))
    times = int(progress/total * 10)
    opptimes = 10 - times

    timesx = '█' * times * 2
    opptimesx = '-' * opptimes * 2

    sys.stdout.flush()
    if times < 10:
        print('\rProgress: [%s%s] %s%% Complete' % (timesx, opptimesx, percent), end=printEnd)

# selector: Allows the user to select   
#           multiple files to be scanned
def selector():
    
    global path_list

    # Textbox that holds file names is cleared
    # Dialog box appears for user to select files to be scanned 
    # and the selected file's paths are passed to a list
    textBox.delete(1.0, tk.END)
    filename = askopenfilenames()
    path_list = list(filename)

    # Filename is extracted from paths and added to textbox
    for name in path_list:
        name = name.split('/')[-1]
        textBox.insert(tk.END, name + "\n")

# regex_finder: returns lines that match regex
def regex_finder(e, exp_line):

    result_list = []
    regex_str = r'(%s)' % e

    result = re.findall(regex_str, exp_line, re.M|re.I)    

    if result:    
        
        result_list.append(exp_line)     
    
    return result_list
        
# set_up: Sets program up for search to begin
def set_up():

    global ambig_list
    global exp_list

    MIN_SIZE = int(comboBox.get())

    print("Loading Model...")
    nlp = spacy.load("en_core_web_lg")
    print("Model Loaded\n")

    # If AmbiguousNames.txt isn't detected in 
    # the Wordlists folder it will be created
    if not os.path.exists(AMBIG_PATH):
        f = open(AMBIG_PATH, 'w')
        f.close()

    # If Result_Logs directory is inexistant one
    # will be created to store the result logs
    if not os.path.exists('Result_Logs/'):
        os.mkdir('Result_Logs/')    

    # Benchmark Timer Start    
    start = time.time()

    # The user selected file's paths are iterated through 
    for path in path_list:

        final_word_list  = []
        final_regex_list = []

        with open(AMBIG_PATH, 'r') as ambiguous, open(REGEX_PATH, 'r') as reg, open(path, 'r') as explanation, open(WORDLIST, 'r') as wl:

            regex = reg.read().splitlines()
            word_list = set(wl.read().splitlines())
            ambig_list = ambiguous.read().splitlines()
            exp_list = explanation.read().splitlines()          

        print("Starting search in: " + path)

        #REGEX SEARCH
        with multiprocessing.Pool(multiprocessing.cpu_count()) as p:

            for result in p.starmap(regex_finder, product(regex, exp_list)):

                if result:

                    final_regex_list = final_regex_list + result

        #NAME SEARCH
        for exp in exp_list:

            progressbar(exp_list.index(exp), len(exp_list))

            exp2 = exp.split('\t', 2)[2]
            doc = nlp(exp2)

            for ent in doc.ents:

                x = ent.label_
                y = ent.text
                if " " in y:
                    z = y.upper().split(" ")
                    temp_set = set(z)
                else:
                    temp_set = {y.upper()}

                if (x == "ORG" or x == "PERSON") and (y not in ambig_list) and (len(y) >= MIN_SIZE) and (temp_set.issubset(word_list)):

                    final_word_list.append(exp + "==" + x + "==" + ent.text)

        # Benchmark Timer End
        end = time.time()
        print('Progress: [████████████████████] 100.0% | Search Completed!')

        # with open('Result_Logs/TIME.txt', 'w') as timer:
        print(f'\nTime to complete: {end - start:.2f}s\n')

        log_name = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S') + " " + path.split('/')[-1]
        
        with open('Result_Logs/TIME' + log_name, 'w') as timer:

            timer.write(f'Time to complete: {end - start:.2f}s\n')

        # Log is created with results of PII found [Naming: log (date) (time) (name of file scanned) .txt]
        with open('Result_Logs/NAMES ' + log_name, 'w+') as y:

            counter = 0

            for result in final_word_list:
                
                y.write("%s\n" % result)

                #Label is added to the result list on the GUI  
                label = tk.Label(scrollable_frame, text=result.split('==')[0], anchor='w')
                button = tk.Button(scrollable_frame, text=result.split('==')[2], anchor='n')
                button.bind("<Button-1>", hide_me)
                button.grid(row=counter, column=0, sticky='ew')
                label.grid(row=counter, column=1, sticky='w')
                counter += 1
        
        with open('Result_Logs/REGEX ' + log_name, 'w+') as y:
            
            for result in final_regex_list:
                
                y.write("%s\n" % result)


################
# GUI Settings #
################
app = tk.Tk()
app.title('PII DETECTOR')
app.geometry("540x525")
button1 = tk.Button(app, text='Select Files', width=20, command=selector)
button2 = tk.Button(app, text='Scan', width=20, command=set_up)
inst_label1 = tk.Label(app, text="Min Word Length", anchor='w')
inst_label2 = tk.Label(app, text="After scan is finished, click on the button with a word you wouldn't like to search for again.", anchor='w', font="Arial 9 bold")
comboBox = ttk.Combobox(app, values=["1", "2","3","4","5","6","7","8"], width=7, justify="center", state="readonly")
comboBox.current(2)
textBox = tk.Text(app, height=4, width=32)

#Scrollable Container Config
container  = tk.Frame(app)
canvas     = tk.Canvas(container, height=300, width=500)
scrollbary = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollbarx = tk.Scrollbar(container, orient="horizontal", command=canvas.xview)
scrollable_frame = tk.Frame(canvas)
scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))    
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)

#Sets widgets in chosen location
def start_screen(): 
    textBox.place(relx=.5, rely=.1, anchor="c")
    button1.place(relx=.5, rely=.22, anchor="c")
    button2.place(relx=.5, rely=.285, anchor="c")
    inst_label1.place(relx=.1, rely=.05, anchor="c")
    inst_label2.place(relx=.5, rely=.34, anchor="c")
    comboBox.place(relx=.1, rely=.1, anchor="c")
    container.place(relx=.5, rely=.68, anchor="c")
    scrollbary.pack(side="right", fill="y")
    scrollbarx.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

#Starts App  
def main(): 
    
    start_screen()
    app.mainloop()

if __name__ == "__main__":
    main()
