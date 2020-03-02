from __future__ import unicode_literals, print_function
from tkinter.filedialog import askopenfilenames
from spacy.util import minibatch, compounding
from spacy.gold import GoldParse
from tkinter import filedialog
from itertools import product
from pathlib import Path
from tkinter import ttk
import multiprocessing
import tkinter as tk
import datetime
import os.path
import random
import spacy
import json
import plac
import time
import sys
import io
import os
import re

####################
# Global Variables #
####################
training_data = []
index_label   = []
path_list     = []
full_line     = ""
training_path = ""
trainingdata  = ""
model_path    = ""

# EDIT AS NEEDED #
AMBIG_PATH = 'Wordlists/AmbiguousNames.txt'
REGEX_PATH = 'Wordlists/REGEX.txt'
WORDLIST   = 'Wordlists/NAMES.txt'

#############
# Functions #
#############

def load_stock_mod():
    global model_path

    model_entry.delete(0, 'end')
    model_path = "en_core_web_lg"
    model_entry.insert(tk.END, "en_core_web_lg")

def load_custom_mod():
    global model_path

    model_entry.delete(0, 'end')
    filename  = filedialog.askdirectory()
    model_path = filename
    print(model_path)
    name = filename.split('/')[-1]
    model_entry.insert(tk.END, name + "\n")

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

    percent  = "{0:.2f}".format(round(((progress/total) * 100),1))
    times    = int(progress/total * 10)
    opptimes = 10 - times

    timesx    = '█' * times * 2
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
    filename  = askopenfilenames()
    path_list = list(filename)

    # Filename is extracted from paths and added to textbox
    for name in path_list:
        name = name.split('/')[-1]
        textBox.insert(tk.END, name + "\n")

# regex_finder: returns lines that match regex
def regex_finder(e, exp_line):

    result_list = []
    regex_str   = r'(%s)' % e

    result = re.findall(regex_str, exp_line, re.M|re.I)    

    if result:    
        
        result_list.append(exp_line)     
    
    return result_list
        
# set_up: Sets program up for search to begin
def set_up():

    ambig_list = []
    exp_list   = []

    # MIN_SIZE dictates the minimum length of the names
    # that get saved into the result list
    MIN_SIZE = int(comboBox.get())

    # Model Load
    print("Loading Model...")
    nlp = spacy.load(model_path)
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
    counter = 0
    
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

                if (x == "ORG" or x == "PERSON") and (len(y) >= MIN_SIZE):
                #if (x == "DATE"):

                    final_word_list.append(exp2 + "==" + x + "==" + ent.text)

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


            name_label = tk.Label(scrollable_frame, text="NAMES", anchor='w')
            name_label.grid(row=counter, column=0, columnspan=2, sticky='ew')
            name_label.config(bg="gray", fg="white")
            counter += 1

            for result in final_word_list:
                
                y.write("%s\n" % result)

                #Label is added to the result list on the GUI  
                label = tk.Label(scrollable_frame, text=result.split('==')[0], anchor='w')
                button = tk.Button(scrollable_frame, text=result.split('==')[2], anchor='n')
                button.bind("<Button-1>", hide_me)
                button.grid(row=counter, column=0, sticky='ew')
                label.grid(row=counter, column=1, sticky='w')

                label2 = tk.Text(scrollable_frame2, height=1, width=150)
                label2.insert(tk.END, result.split('==')[0])
                button2 = tk.Button(scrollable_frame2, text='CORR', anchor='n')
                button2.bind("<Button-1>", hide_me_too)
                button2.grid(row=counter, column=0, sticky='ew')
                label2.grid(row=counter, column=1, sticky='w')
                counter += 1
        
        with open('Result_Logs/REGEX ' + log_name, 'w+') as y:
            
            regex_label = tk.Label(scrollable_frame, text="REGEX", anchor='w')
            regex_label.grid(row=counter, column=0, columnspan=2, sticky='ew')
            regex_label.config(bg="gray", fg="white")

            counter += 1

            for result in final_regex_list:
                
                y.write("%s\n" % result)
                
                label = tk.Label(scrollable_frame, text=result, anchor='w')
                label.grid(row=counter, column=0, columnspan=2, sticky='w')
                counter += 1

#############################################
# PREPARE TAB
#############################################
def index_labeler(event):

    global index_label
    global full_line

    os.system("cls")
    
    widget = app.focus_get() 

    full_line = widget.get("1.0",tk.END).rstrip()
    print(full_line)
    line = widget.selection_get()

    s0 = int(widget.index("sel.first").split('.',1)[1])
    s1 = int(widget.index("sel.last").split('.',1)[1])
    label = event.widget.cget('text')

    tup = [s0, s1, label]
    index_label.append(tup)

    print(index_label)

def hide_me_too(event):

    global index_label

    if index_label:
        list_in_row = scrollable_frame2.grid_slaves(row=int(event.widget.grid_info()['row']))
        
        for i in list_in_row:
            i.grid_forget()

        tup = [full_line, {"entities": index_label}]

        index_label = []

        training_data.append(tup)
        print(training_data)
    else:
        print("You haven't selected any data to train with\n")

def index_undo():
    if index_label:
        index_label.pop()
        print(index_label)
    else:
        print("You haven't selected any data to train with\n")

def undo():
    if training_data:
        training_data.pop()
        print(training_data)
    else:
        print("You have no training data\n")

def done():

    if not os.path.exists('Training_Data/'):
        os.mkdir('Training_Data/')    

    data_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    with open('Training_Data/TrainingData ' + data_time + '.json','w+') as y:
    
        json.dump(training_data, y)

    n.select(f3)
    print("Saved to Training_Data directory as TrainingData " + data_time + '.txt')

#############################################
# TRAIN TAB
#############################################
def load_stock():
    global training_path

    old_model_name_etry.delete(0, 'end')
    training_path = "en_core_web_lg"
    old_model_name_etry.insert(tk.END, "en_core_web_lg")

def load_custom():
    global training_path

    old_model_name_etry.delete(0, 'end')
    filename  = filedialog.askdirectory()
    training_path = filename
    print(training_path)
    name = filename.split('/')[-1]
    old_model_name_etry.insert(tk.END, name + "\n")

def load_data():
    global trainingdata
    filename  = askopenfilenames()
    trainingdata = filename
    path_list = list(filename)

    # Filename is extracted from paths and added to textbox
    for name in path_list:
        trainingdata = name
        with open(name, 'r') as fl:

            x = fl.read().splitlines()

            for y in x:
                model_train_data.insert(tk.END, y)
                model_train_data.insert(tk.END, '\n')

def train_model():

    REVISION_DATA = []
    revision_texts = []

    model = training_path
    new_mod_name = model_name_etry.get()
    n_iter=100

    #Create Dir for new model
    if new_mod_name != '':
        output_dir = 'Custom_Models/' + new_mod_name
    else:
        print("Choose model name")
        return

    #Load revision data from file
    with open('Wordlists/REVISION_DATA.txt', 'r') as x:

        revision_texts = x.read().splitlines()

    if trainingdata != '':

        #Load training data from file
        with io.open(trainingdata, encoding='utf8') as f:
            TRAIN_DATA = json.load(f)

        #Train
        if model != '':

            os.mkdir(output_dir)
            print("Loading model...")
            nlp = spacy.load(model)  # load existing spaCy model
            print("Loaded model '%s'" % model)

            # create the built-in pipeline components and add them to the pipeline
            # nlp.create_pipe works for built-ins that are registered with spaCy
            if "ner" not in nlp.pipe_names:
                ner = nlp.create_pipe("ner")
                nlp.add_pipe(ner, last=True)
            # otherwise, get it so we can add labels
            else:
                ner = nlp.get_pipe("ner")

            # add labels
            for _, annotations in TRAIN_DATA:
                for ent in annotations.get("entities"):
                    ner.add_label(ent[2])

            for doc in nlp.pipe(revision_texts):
                entities = [(e.start_char, e.end_char, e.label_) for e in doc.ents]
                REVISION_DATA.append((doc, GoldParse(doc, entities=entities)))

            # get names of other pipes to disable them during training
            pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
            other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
            with nlp.disable_pipes(*other_pipes):  # only train NER
                # reset and initialize the weights randomly – but only if we're
                # training a new model
                if model is None:
                    nlp.begin_training()
                for itn in range(n_iter):
                    examples = REVISION_DATA + TRAIN_DATA
                    losses = {}
                    random.shuffle(examples)
                    # batch up the examples using spaCy's minibatch
                    batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
                    for batch in batches:
                        texts, annotations = zip(*batch)
                        nlp.update(
                            texts,  # batch of texts
                            annotations,  # batch of annotations
                            drop=0.5,  # dropout - make it harder to memorise data
                            losses=losses,
                        )
                    print("Losses", losses)

            # test the trained model
            for text, _ in TRAIN_DATA:
                doc = nlp(text)
                print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
                print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])

            # save model to output directory
            if output_dir is not None:
                output_dir = Path(output_dir)
                if not output_dir.exists():
                    output_dir.mkdir()
                nlp.to_disk(output_dir)
                print("Saved model to", output_dir)
        else:
            print("Choose a model to train")
    else:
        print("Choose training data")

def regex_edit():
    os.startfile('Wordlists\REGEX.txt')


################
# GUI Settings #
################
app = tk.Tk()
app.title('PII DETECTOR')
app.geometry("1150x545")

#Notebook(Tabs) Settings
n = ttk.Notebook(app)
n.grid(row=0, column=0, sticky='ew')
f1 = ttk.Frame(n, width=1140, height=525)  
f2 = ttk.Frame(n, width=1140, height=525)
f3 = ttk.Frame(n, width=1140, height=525)
n.add(f1, text='        FIND        ')
n.add(f2, text='       PREPARE       ')
n.add(f3, text='       TRAIN       ')

#Finder Settings
model_btn1 = tk.Button(f1, text='Custom Model', width=17, command=load_custom_mod)
model_btn2 = tk.Button(f1, text='Stock Model', width=17, command=load_stock_mod)
model_entry = tk.Entry(f1, width=42)

button1 = tk.Button(f1, text='Select Files', width=17, command=selector)
button2 = tk.Button(f1, text='Scan', width=17, command=set_up)
inst_label1 = tk.Label(f1, text="Min Word Length", anchor='w')
inst_label2 = tk.Label(f1, text="After scan is finished, click on the button with a word you wouldn't like to search for again.", anchor='w', font="Arial 9 bold")
comboBox = ttk.Combobox(f1, values=["1", "2","3","4","5","6","7","8"], width=7, justify="center", state="readonly")
comboBox.current(2)
textBox = tk.Text(f1, height=4, width=32)

regex_button = tk.Button(f1, text='Edit REGEX', width=17, command=regex_edit)

#Scrollable Container Config
container  = tk.Frame(f1)
canvas     = tk.Canvas(container, height=500, width=850)
scrollbary = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollbarx = tk.Scrollbar(container, orient="horizontal", command=canvas.xview)
scrollable_frame = tk.Frame(canvas)
scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))    
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)

#Prepare Settings
textBox1  = tk.Text(f2, height=18, width=50)
textBox2  = tk.Text(f2, height=1, width=50)

button0T  = tk.Button(f2, text='CORR', anchor='n')
button1T  = tk.Button(f2, text='PERSON', width=12)
button2T  = tk.Button(f2, text='NORP', width=12)
button3T  = tk.Button(f2, text='FAC', width=12)
button4T  = tk.Button(f2, text='ORG', width=12)
button5T  = tk.Button(f2, text='GPE', width=12)
button6T  = tk.Button(f2, text='LOC', width=12)
button7T  = tk.Button(f2, text='PRODUCT', width=12)
button8T  = tk.Button(f2, text='EVENT', width=12)
button9T  = tk.Button(f2, text='WORK_OF_ART', width=12)
button10T = tk.Button(f2, text='LAW', width=12)
button11T = tk.Button(f2, text='LANGUAGE', width=12)
button12T = tk.Button(f2, text='DATE', width=12)
button13T = tk.Button(f2, text='TIME', width=12)
button14T = tk.Button(f2, text='PERCENT', width=12)
button15T = tk.Button(f2, text='MONEY', width=12)
button16T = tk.Button(f2, text='QUANTITY', width=12)
button17T = tk.Button(f2, text='ORDINAL', width=12)
button18T = tk.Button(f2, text='CARDINAL', width=12)

button_undo = tk.Button(f2, text='UNDO', width=20, command=undo)
button_undo2 = tk.Button(f2, text='UNDO INDEXING', width=20, command=index_undo)
button_done = tk.Button(f2, text='DONE', width=20, command=done)

button0T.bind("<Button-1>", hide_me_too)
button1T.bind("<Button-1>", index_labeler)
button2T.bind("<Button-1>", index_labeler)
button3T.bind("<Button-1>", index_labeler)
button4T.bind("<Button-1>", index_labeler)
button5T.bind("<Button-1>", index_labeler)
button6T.bind("<Button-1>", index_labeler)
button7T.bind("<Button-1>", index_labeler)
button8T.bind("<Button-1>", index_labeler)
button9T.bind("<Button-1>", index_labeler)
button10T.bind("<Button-1>", index_labeler)
button11T.bind("<Button-1>", index_labeler)
button12T.bind("<Button-1>", index_labeler)
button13T.bind("<Button-1>", index_labeler)
button14T.bind("<Button-1>", index_labeler)
button15T.bind("<Button-1>", index_labeler)
button16T.bind("<Button-1>", index_labeler)
button17T.bind("<Button-1>", index_labeler)
button18T.bind("<Button-1>", index_labeler)

#Scrollable Container Config
container2  = tk.Frame(f2)
canvas2     = tk.Canvas(container2, height=395, width=1100)
scrollbary2 = tk.Scrollbar(container2, orient="vertical", command=canvas2.yview)
scrollbarx2 = tk.Scrollbar(container2, orient="horizontal", command=canvas2.xview)
scrollable_frame2 = tk.Frame(canvas2)
scrollable_frame2.bind("<Configure>",lambda e: canvas2.configure(scrollregion=canvas2.bbox("all")))    
canvas2.create_window((0, 0), window=scrollable_frame2, anchor="nw")
canvas2.configure(yscrollcommand=scrollbary2.set, xscrollcommand=scrollbarx2.set)

#TRAIN
model_name_lbl   = tk.Label(f3, text=" New Model Name:", anchor='w')
model_name_etry  = tk.Entry(f3)

old_model_name_lbl = tk.Label(f3, text="Model to train:", anchor='w')
old_model_name_etry = tk.Entry(f3)
load_model    = tk.Button(f3, text="Load Custom Model", command=load_custom)
stock_model  = tk.Button(f3, text="Load Stock Model", command=load_stock)

model_train_data = tk.Text(f3, height=32, width=115)
load_data_btn    = tk.Button(f3, text="Load Data", command=load_data)
train_model_btn  = tk.Button(f3, text="Train Model", command=train_model)

#Sets widgets in chosen location
def start_screen(): 

    #FIND
    textBox.grid(row=0, column=0, columnspan=2, sticky="nw")
    model_btn1.grid(row=1, column=0, sticky="nw")
    model_btn2.grid(row=1, column=1, sticky="nw")
    model_entry.grid(row=2, column=0, columnspan=2, sticky="nw")
    button1.grid(row=4, column=0, sticky="nw")
    button2.grid(row=4, column=1, sticky="nw")
    inst_label1.grid(row=3, column=0, sticky="nw")
    comboBox.grid(row=3, column=1, sticky="nw")
    regex_button.grid(row=5, column=0, sticky="nw")
    container.grid(row=0, column=2, sticky="ew", rowspan=100)
    scrollbary.pack(side="right", fill="y")
    scrollbarx.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

    #PREPARE
    container2.grid(row=0, column=0, sticky='ew', columnspan=20)
    scrollbary2.pack(side="right", fill="y")
    scrollbarx2.pack(side="bottom", fill="x")
    canvas2.pack(side="left", fill="both", expand=True)
    textBox2.grid(row=4, column=1, sticky='ew', columnspan=20)
    textBox2.insert(tk.END, "(Insert Custom Training Data here)")
    button0T.grid(row=4, column=0, sticky='ew')
    button1T.grid(row=5, column=0, sticky='ew')
    button2T.grid(row=6, column=0, sticky='ew')
    button7T.grid(row=5, column=1, sticky='ew')
    button8T.grid(row=6, column=1, sticky='ew')
    button13T.grid(row=5, column=2, sticky='ew')
    button14T.grid(row=6, column=2, sticky='ew')
    button6T.grid(row=5, column=3, sticky='ew')
    button5T.grid(row=6, column=3, sticky='ew')
    button17T.grid(row=5, column=4, sticky='ew')
    button18T.grid(row=6, column=4, sticky='ew')
    button4T.grid(row=5, column=5, sticky='ew')
    button10T.grid(row=6, column=5, sticky='ew')
    button3T.grid(row=5, column=6, sticky='ew')
    button9T.grid(row=5, column=7, sticky='ew')
    button15T.grid(row=5, column=8, sticky='ew')
    button11T.grid(row=6, column=6, sticky='ew')
    button12T.grid(row=6, column=7, sticky='ew')
    button16T.grid(row=6, column=8, sticky='ew')
    button_undo2.grid(row=8, column=2, sticky='ew', columnspan=2)
    button_undo.grid(row=8, column=4, sticky='ew', columnspan=2)
    button_done.grid(row=8, column=6, sticky='ew', columnspan=2)

    #TRAIN
    model_train_data.grid(row=0, column=2, rowspan=20)
    model_name_lbl.grid(row=0, column=0)
    model_name_etry.grid(row=0, column=1)
    load_data_btn.grid(row=3, column=0)
    train_model_btn.grid(row=3, column=1)
    
    old_model_name_lbl.grid(row=1, column=0)
    old_model_name_etry.grid(row=1, column=1)
    load_model.grid(row=2, column=0)
    stock_model.grid(row=2, column=1)

#Starts App  
def main(): 
    
    start_screen()
    app.mainloop()

if __name__ == "__main__":
    main()
