import openai
import os
import xml.etree.ElementTree as ET

openai.api_key = os.getenv("OPENAI_API_KEY")


def get_note(path):
    '''
    Gets text body of xml clinical note

    path: relative path to the .xml clinical note to parse
    '''
    root = ET.parse(path).getroot()
    text = root.find('TEXT').text.strip()
    return text


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

# gpt-3.5-turbo-16k


def split_and_tag_xml_file(input_xmlfile, output_folder):
    '''
    Splits the input XML file into two equal halves, applies tags to them,
    and saves the resulting halves in the output folder.

    input_file: the path to the input XML file
    output_folder: the folder where the resulting halves will be saved
    '''

    # Get the text body of the XML clinical note
    note = get_note(input_xmlfile)

    # Calculate the midpoint of the note text
    midpoint = len(note) // 2

    # Split the note into two equal halves
    first_half_note = note[:midpoint]
    second_half_note = note[midpoint:]

    # Parse the input XML file
    tree = ET.parse(input_xmlfile)
    root = tree.getroot()

    # Find the TAGS element
    tags_element = root.find('TAGS')

    # Create two new XML elements for the first and second halves
    first_half_element = ET.Element('deIdi2b2')
    text_element = ET.SubElement(first_half_element, 'TEXT')
    text_element.text = first_half_note + "\n"
    tags_element_first_half = ET.SubElement(first_half_element, 'TAGS')
    # Copy the tags from the original
    tags_element_first_half.extend(tags_element[:])

    second_half_element = ET.Element('deIdi2b2')
    text_element = ET.SubElement(second_half_element, 'TEXT')
    text_element.text = second_half_note + "\n"
    tags_element_second_half = ET.SubElement(second_half_element, 'TAGS')
    # Copy the tags from the original
    tags_element_second_half.extend(tags_element[:])

    # Create file names for the first and second halves
    base_file_name = os.path.splitext(os.path.basename(input_xmlfile))[0]
    first_half_file_name = f'{base_file_name}_p01.xml'
    second_half_file_name = f'{base_file_name}_p02.xml'

    # Create paths for output files
    first_half_output_path = os.path.join(output_folder, first_half_file_name)
    second_half_output_path = os.path.join(
        output_folder, second_half_file_name)

    # Create two new XML files for the first and second halves
    first_half_tree = ET.ElementTree(first_half_element)
    second_half_tree = ET.ElementTree(second_half_element)

    # Write the first and second halves to separate XML files
    first_half_tree.write(first_half_output_path,
                          encoding='utf-8', xml_declaration=True)
    second_half_tree.write(second_half_output_path,
                           encoding='utf-8', xml_declaration=True)


def split_and_tag_xml_files(input_folder, output_folder):
    '''
    Splits each XML file in the input folder into two equal halves,
    applies tags to them, and saves the resulting halves in the output folder.

    input_folder: the folder containing the input XML files
    output_folder: the folder where the resulting halves will be saved
    '''

    file_list = iterate_dir(input_folder)

    for input_file in file_list:
        split_and_tag_xml_file(input_file, output_folder)


if __name__ == "__main__":
    # Replace with the path to your input folder containing XML files
    input_folder = 'ground_truth/training-PHI-Gold-Set2'
    # Replace with the path where you want to save the resulting halves
    output_folder = 'training_2_phi_split'
    os.makedirs(output_folder, exist_ok=True)
    split_and_tag_xml_files(input_folder, output_folder)
