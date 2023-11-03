import xml.etree.ElementTree as ET
import openai
import os


def anonymize_text_with_tags(file_path):
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Find the TAGS element and get its child tags
    tags_element = root.find('TAGS')
    if tags_element is not None:
        tags = tags_element.findall('*')

        # Find the TEXT element and get its content
        text_element = root.find('TEXT')
        if text_element is not None:
            text = text_element.text

            # Anonymize date tags in the TEXT section
            for tag in tags:
                if tag.tag == 'DATE':
                    tag_id = tag.get('id')
                    tag_type = tag.get('TYPE')
                    tag_text = tag.get('text')
                    text = text.replace(tag_text, f'[REDACTED]')

                elif tag.tag == 'AGE':
                    tag_id = tag.get('id')
                    tag_text = tag.get('text')
                    text = text.replace(tag_text, f'[REDACTED]')

                elif tag.tag == 'DOCTOR':
                    tag_id = tag.get('id')
                    tag_text = tag.get('text')
                    text = text.replace(tag_text, f'[REDACTED]')
                elif tag.tag == 'NAME':
                    tag_id = tag.get('id')
                    tag_text = tag.get('text')
                    text = text.replace(tag_text, f'[REDACTED]')
                elif tag.tag == 'LOCATION':
                    tag_id = tag.get('id')
                    tag_text = tag.get('text')
                    text = text.replace(tag_text, f'[REDACTED]')
                elif tag.tag == 'CONTACT':
                    tag_id = tag.get('id')
                    tag_text = tag.get('text')
                    text = text.replace(tag_text, f'[REDACTED]')
                elif tag.tag == 'PROFESSION':
                    tag_id = tag.get('id')
                    tag_text = tag.get('text')
                    text = text.replace(tag_text, f'[REDACTED]')
                elif tag.tag == 'ID':
                    tag_id = tag.get('id')
                    tag_text = tag.get('text')
                    text = text.replace(tag_text, f'[REDACTED]')

            # Update the anonymized text in the XML tree
            text_element.text = text

        # Save the updated XML to a new file (optional)
        tree.write('anonymized_file.xml',
                   encoding='UTF-8', xml_declaration=True)

        return text_element.text


def iterate_dir(folder):
    '''
    iterate over files in the 'folder' directory (assuming its in the cwd)
    and return a list of the relative paths of all the files in that folder

    folder: the folder of .xml clinical notes you want to iterate over
    '''
    names = []
    for filename in os.listdir(folder):
        f = os.path.join(folder, filename)
        # checking if it is a file
        if os.path.isfile(f):
            names += [f]
    return names


def create_anonymized_notes_with_tags(list_of_files):
    '''
    Creates a new folder of the anonymized clinical notes. After creating
    the new directory, it creates .txt files whose name corresponds to
    the .xml file of the same name from the specified folder of unanonymized
    clinincal notes. It fills each .txt file with the anonymized body of the 
    clinical note. Right now, there is a counter to only complete a few notes.

    list_of_files: a list containing each of the relative paths of the .xml
    clinical notes (use iterate_dir() to create this)
    '''

    # counter = 0

    old_dir = os.getcwd()  # get current directory
    folder_name = 'TAG-RESULTS-' + list_of_files[0].split('/')[0]
    os.mkdir('./' + folder_name)  # create RESULTS directory

    for file in list_of_files:
        note = anonymize_text_with_tags(file)
        # prompt = create_prompt(note)
        # completion = get_completion(prompt)
        new_file_name = file.split('/')[-1].split('.')[0] + '.txt'
        os.chdir(os.path.join(old_dir, folder_name))
        f = open(new_file_name, 'w')
        f.write(note)
        os.chdir(old_dir)

        # counter += 1
        # if counter == 50:
        #     break
    pass


# anonymize_text_with_tags('training-PHI-Gold-Set1/395-04.xml')
create_anonymized_notes_with_tags(iterate_dir('training-PHI-Gold-Set1'))

# import openai
# import os
# import xml.etree.ElementTree as ET

# openai.api_key = os.getenv("OPENAI_API_KEY")

# def create_prompt(note):
#     prompt = f'''
#     print out the given text

#     """{note}"""
#     '''
#     return prompt

# def get_note(path):
#     '''
#     Gets text body of xml clinical note

#     path: relative path to the .xml clinical note to parse
#     '''
#     root = ET.parse(path).getroot()
#     text = root.find('TAGS') #.text.strip()
#     if text is not None:
#         # Create a new XML tree containing only the TAGS element
#         tags_tree = ET.ElementTree(text)
#         # Save the TAGS section to a new file (optional)
#         #tags_tree.write('tags_section.xml', encoding='UTF-8', xml_declaration=True)

#     return tags_tree

# def iterate_dir(folder):
#     '''
#     iterate over files in the 'folder' directory (assuming its in the cwd)
#     and return a list of the relative paths of all the files in that folder

#     folder: the folder of .xml clinical notes you want to iterate over
#     '''
#     names = []
#     for filename in os.listdir(folder):
#         f = os.path.join(folder, filename)
#         # checking if it is a file
#         if os.path.isfile(f):
#             names += [f]
#     return names

# def get_completion(prompt, model="gpt-3.5-turbo"):
#     '''
#     Gets completion from specified openai model

#     prompt: the prompt to feed the model
#     model: the OpenAI model to use
#     '''
#     messages = [{"role": "user", "content": prompt}]
#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=messages,
#         temperature=0
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

#     old_dir = os.getcwd() # get current directory
#     folder_name = 'TAGS-' + list_of_files[0].split('/')[0]
#     os.mkdir('./' + folder_name) # create RESULTS directory

#     for file in list_of_files:
#         note = get_note(file)
#         prompt = create_prompt(note)
#         completion = get_completion(prompt)
#         new_file_name = file.split('/')[-1].split('.')[0] + '.txt'
#         os.chdir(os.path.join(old_dir, folder_name))
#         f = open(new_file_name, 'w')
#         f.write(completion)
#         os.chdir(old_dir)

#         counter += 1
#         if counter == 1:
#             break
#     pass

# # single function call
# create_anonymized_notes(iterate_dir('training-PHI-Gold-Set1'))
