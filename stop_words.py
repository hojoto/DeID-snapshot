from distutils.command.clean import clean
from gpt_redact_v2 import iterate_dir
import xml.etree.ElementTree as ET
import openai
import os

import nltk
from nltk.corpus import stopwords

import random

openai.api_key = os.getenv("OPENAI_API_KEY")
# export OPENAI_API_KEY='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'
# try and batch data and see if that works better


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
    # print(tags_global) #tags_global is correct
    # return tags

    # ans_root = ET.parse(answer_path).getroot()
    # tags = ans_root.find('TAGS').findall('*')

    # for tag in tags:
    #     tag_type = tag.get('TYPE')
    #     tag_text = tag.get('text')


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
        if os.path.isfile(f):
            names += [f]
    return names


# remove stop words
def remove_stop_words(file):

    stop_words = set(stopwords.words('english'))

    text = file
    lines = text.splitlines()
    new_text = []
    for line in lines:
        words = line.split()
        clean_words = [word for word in words if word.lower()
                       not in stop_words]
        new_text.append(' '.join(clean_words))
    return '\n'.join(new_text)

# global tags
# tags_global = []

def random_removal(file):
    percentage = .90  # could move this to an input later
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
    print(non_removed_words)

    for line in lines:
        words = line.split()
        clean_words = [word for word in words if word.lower()
                       not in non_removed_words]
        new_text.append(' '.join(clean_words))

    return '\n'.join(new_text)
    
    
    # print(tags_global) #this is corrrect
    # for line in lines:
    #    for word in line.split():
    #        if word not in tags_global:
    #             removed_words.append(word)
    # for line in text.splitlines():
    #     for word in line.split():
    # for line in text.splitlines():
    #     for word in line.split():
    #         if word not in non_removed_words:
    #             clean_words.append(word)
    # new_text.append(' '.join(clean_words))
    
    # for line in lines:
    #     # words = line.split()
    #     clean_words = [word for word in line.split() if word in non_removed_words]
    #     new_text.append(' '.join(clean_words))

def create_stop_word_free(list_of_files):

    old_dir = os.getcwd()  # get current directory
    folder_name = 'removal_test1' + list_of_files[0].split('/')[0]
    os.mkdir('./' + folder_name)  # create RESULTS directory
    
    for file in list_of_files:
        get_tags(file) #dont need this for stop word removal
        note = random_removal(get_note(file)) #can call relevant function here!!
        new_file_name = file.split('/')[-1].split('.')[0] + '.txt'
        os.chdir(old_dir + '/' + folder_name)
        f = open(new_file_name, 'w')
        f.write(note)
        os.chdir(old_dir)


if __name__ == "__main__":
    create_stop_word_free(iterate_dir('stop_test'))
