from http.client import responses
import openai
import os
import xml.etree.ElementTree as ET

import nltk
from nltk.corpus import stopwords

import random

openai.api_key = os.getenv("OPENAI_API_KEY")
# export OPENAI_API_KEY='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'
# try and batch data and see if that works better

#change temperature back to 0!

def create_prompt(note):
    prompt = f'''
    Task: Please anonymize the clinical note delimited by triple quotes of any
Protected Health Information according to the HIPAA Privacy Rule.


Specifications:
- Replace any text that could be classified as one of the
18 HIPAA identifiers with [REDACTED].
- The 18 HIPAA identifiers are listed in this prompt and they are delimited by triple slashes.
- Your response should be the modified clinical note with all protected health
information replaced with [REDACTED].
- Remove the triple quotes from your final response.
- Do not remove any whitespace found in the original text, such as newline characters or tabs,
from your response.


///
1) Name
2) Address (all geographic subdivisions smaller than state, including street address, city county, and zip code)
3) All elements (except years) of dates related to an individual (including birthdate, admission date, discharge date, date of death, and exact age if over 89)
4) Telephone numbers
5) Fax number
6) Email address
7) Social Security Number
8) Medical record number
9) Health plan beneficiary number
10) Account number
11) Certificate or license number
12) Vehicle identifiers and serial numbers, including license plate numbers
13) Device identifiers and serial numbers
14) Web URL
15) Internet Protocol (IP) Address
16) Finger or voice print
17) Photographic image - Photographic images are not limited to images of the face.
18) Any other characteristic that could uniquely identify the individual
///


    """{note}""" 
    '''
    return prompt


def get_note(path):
    '''
    Gets text body of xml clinical note

    path: relative path to the .xml clinical note to parse
    '''
    
    root = ET.parse(path).getroot()
    text = root.find('TEXT').text.strip()
    return text

    

tags_global = []
#not actually getting any tags
def get_tags(path):
    root = ET.parse(path).getroot()
    tags = root.find('TAGS').findall('*')
    for tag in tags:
        tag_text = tag.get('text')
        tag_text = tag_text.split()
        for tag in tag_text:
            tags_global.append(tag)
    # print(tags_global) #tags_global is 

def iterate_dir(filepath):
    '''
    iterate over files in the 'folder' directory (assuming its in the cwd)
    and return a list of the relative paths of all the files in that folder

    folder: the folder of .xml clinical notes you want to iterate over
    '''
    names = []
    for filename in os.listdir(filepath):
        f = os.path.join(filepath, filename)
        # checking if it is a file

        #mac creates a ds.store which is an issue because it not a valid xml
        if os.path.isfile(f) and filename.endswith('.xml'):
            names += [f]
    return names

# gpt-3.5-turbo-16k


def get_completion(prompt, model="gpt-4"):
    '''
    Gets completion from specified openai model

    prompt: the prompt to feed the model
    model: the OpenAI model to use
    '''
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0 #i think 0 is best but changing this
    )
    return response.choices[0].message["content"]

#-------------------------------------------------------------

def remove_stop_words(file):

    stop_words = set(stopwords.words('english'))
   
    text = file
    lines = text.splitlines()
    new_text = []
    for line in lines:
        words = line.split()
        clean_words = [word for word in words if word.lower() not in stop_words]
        new_text.append(' '.join(clean_words))
    return '\n'.join(new_text)
   
#--------------------------
#-------------------------------------------------------------
def random_removal(file):
    percentage = .50  # could move this to an input later
    text = file

    num_words = text.split()
    lines = text.splitlines()
    remove_num = int(percentage * len(num_words))
    random.seed(10) #not totally sure what to make the seed number --> maybe make it remove_num
    # removed_words = random.sample(num_words, remove_num)

    #ALSO need to split PHI!!!!! (In basic failure anlaysis too this way each word is one phi even or a two word name)
    new_text = []
    non_removed_words = []

    for word in text.split():
        if word not in tags_global:
            non_removed_words.append(word)
    # print(non_removed_words)
    non_removed_words = random.sample(non_removed_words, remove_num) #should be taking a sample from everything but phi

    clean_words = []
    # print(non_removed_words)

    for line in lines:
        words = line.split()
        clean_words = [word for word in words if word.lower()
                       not in non_removed_words]
        new_text.append(' '.join(clean_words))

    return '\n'.join(new_text)

def create_anonymized_notes(list_of_files):
    '''
    Creates a new folder of the anonymized clinical notes. After creating
    the new directory, it creates .txt files whose name corresponds to
    the .xml file of the same name from the specified folder of unanonymized
    clinincal notes. It fills each .txt file with the anonymized body of the 
    clinical note. Right now, there is a counter to only complete a few notes.

    list_of_files: a list containing each of the relative paths of the .xml
    clinical notes (use iterate_dir() to create this)
    '''

    counter = 0

    old_dir = os.getcwd()  # get current directory
    folder_name = 'ugh_full_random50' + list_of_files[0].split('/')[0]
    os.mkdir('./' + folder_name)  # create RESULTS directory

    for file in list_of_files:
        # get_tags_removal(file) //uncomment for random removal
        file_count = 1
        print("current file: ")
        print(file)
        file_count += 1 #find out where this line should go to make things a little more readable
        note = get_note(file)
        cleaned_note = random_removal(note) #uncomment for stop word or random removal testing
        prompt = create_prompt(cleaned_note) #replace with cleaned_note for stop/random word removal
        completion = get_completion(prompt)
        new_file_name = file.split('/')[-1].split('.')[0] + '.txt'
    
        # file_count += 1 #find out where this line should go to make things a little more readable
        os.chdir(old_dir + '/' + folder_name)
        f = open(new_file_name, 'w')
        f.write(completion)
        os.chdir(old_dir)

        # print("Finished file #" + str(file_count))
        # file_count += 1
        # counter += 1
        # if counter == 5:
        #     break

if __name__ == "__main__":
    # single function call
    # batch_size = 20
    #see about batching the iterate_dir function

    create_anonymized_notes(iterate_dir('ground_truth/207_tests')) #ground_truth/new_sample_files_truth


#------------------------------------
# import openai
# import os
# import xml.etree.ElementTree as ET

# openai.api_key = os.getenv("OPENAI_API_KEY")
# # export OPENAI_API_KEY='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'
# # try and batch data and see if that works better

# # change temperature back to 0!




# def create_prompt(note):
#     prompt = f'''
#     Task: Please anonymize the clinical note delimited by triple quotes of any
# Protected Health Information according to the HIPAA Privacy Rule.

# Specifications:
# - Replace any text that could be classified as one of the
# 18 HIPAA identifiers with [REDACTED].
# - The 18 HIPAA identifiers are listed in this prompt and they are delimited by triple slashes.
# - Your response should be the modified clinical note with all protected health
# information replaced with [REDACTED].
# - Remove the triple quotes from your final response.
# - Do not remove any whitespace found in the original text, such as newline characters or tabs,
# from your response.

# ///
# 1) Name
# 2) Address (all geographic subdivisions smaller than state, including street address, city county, and zip code)
# 3) All elements (except years) of dates related to an individual (including birthdate, admission date, discharge date, date of death, and exact age if over 89)
# 4) Telephone numbers
# 5) Fax number
# 6) Email address
# 7) Social Security Number
# 8) Medical record number
# 9) Health plan beneficiary number
# 10) Account number
# 11) Certificate or license number
# 12) Vehicle identifiers and serial numbers, including license plate numbers
# 13) Device identifiers and serial numbers
# 14) Web URL
# 15) Internet Protocol (IP) Address
# 16) Finger or voice print
# 17) Photographic image - Photographic images are not limited to images of the face.
# 18) Any other characteristic that could uniquely identify the individual
# ///

#     """{note}""" 
#     '''
#     return prompt
# #took out of prompt:
# # At the end of the note please produce the following:
# #         - your confidence in the results
# #         - a list of all of the information you were unsure about. Please include at least one item in this list


# def get_note(path):
#     '''
#     Gets text body of xml clinical note

#     path: relative path to the .xml clinical note to parse
#     '''
#     root = ET.parse(path).getroot()
#     text = root.find('TEXT').text.strip()
#     return text


# def iterate_dir(filepath):
#     '''
#     iterate over files in the 'folder' directory (assuming its in the cwd)
#     and return a list of the relative paths of all the files in that folder

#     folder: the folder of .xml clinical notes you want to iterate over
#     '''
#     names = []
#     for filename in os.listdir(filepath):
#         f = os.path.join(filepath, filename)
#         # checking if it is a file
#         if os.path.isfile(f):
#             names += [f]
#     return names

# # gpt-3.5-turbo-16k


# def get_completion(prompt, model="gpt-4"):
#     '''
#     Gets completion from specified openai model

#     prompt: the prompt to feed the model
#     model: the OpenAI model to use
#     '''
#     messages = [{"role": "user", "content": prompt}]
#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=messages,
#         temperature=0 #i think 0 is best but changing this
#     )
#     return response.choices[0].message["content"]


# def create_anonymized_notes(list_of_files):
#     '''
#     Creates a new folder of the anonymized clinical notes. After creating
#     the new directory, it creates .txt files whose name corresponds to
#     the .xml file of the same name from the specified folder of unanonymized
#     clinincal notes. It fills each .txt file with the anonymized body of the 
#     clinical note. Right now, there is a counter to only complete a few notes.

#     list_of_files: a list containing each of the relative paths of the .xml
#     clinical notes (use iterate_dir() to create this)
#     '''

#     counter = 0

#     old_dir = os.getcwd()  # get current directory
#     folder_name = 'new_files_test4' + list_of_files[0].split('/')[0]
#     os.mkdir('./' + folder_name)  # create RESULTS directory

#     for file in list_of_files:
#         note = get_note(file)
#         prompt = create_prompt(note)
#         completion = get_completion(prompt)
#         new_file_name = file.split('/')[-1].split('.')[0] + '.txt'
#         os.chdir(old_dir + '/' + folder_name)
#         f = open(new_file_name, 'w')
#         f.write(completion)
#         os.chdir(old_dir)

#         # counter += 1
#         # if counter == 5:
#         #     break
#     pass


# if __name__ == "__main__":
#     # single function call
#     # batch_size = 20
#     #see about batching the iterate_dir function

#     create_anonymized_notes(iterate_dir('ground_truth/new_sample_files_truth'))