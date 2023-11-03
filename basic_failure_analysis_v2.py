from logging.handlers import TimedRotatingFileHandler
from gpt_redact_v2 import iterate_dir
import xml.etree.ElementTree as ET
import re

import openai
import os

# global vars for counting
error_numbers = {}
type_numbers = {}
tot_false_neg = 0
tot_false_pos = 0
tot_true_neg = 0
tot_true_pos = 0


def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def compare(gpt_path, answer_path):
    # ALSO need to split PHI!!!!! (this way each word is one phi even or a two word name)

    # xml tree stuff
    ans_root = ET.parse(answer_path).getroot()
    tags = ans_root.find('TAGS').findall('*')
    gt_text = ans_root.find('TEXT').text
    text = read_text_file(gpt_path)
    # print(gt_text)

    errors = {}
    under_redact = 0
    over_redact = 0
    # len(tags)  # expected; correct --> but need to account for multi word tags
    total_redact = 0
    # total_words = len(text.split())
    # gt_text = gt_text.split()
    # #WITHOUT RANDOM:
    # final_gt_text = re.findall(r'\b\w+\b', gt_text)
    # total_words = len(final_gt_text)#len(text.split())
    #---------

    #With random removal:
    total_words = len(text.split())
    print("total words: \n")
    print(total_words)
    true_neg = 0

    # calculate expected redact
    for tag in tags:
        tag_text = tag.get('text')
        total_redact += len(tag_text.split())  # expected
    print("total redact")
    print(total_redact)

    # count total words that are not redacted (to calculate true negatives)
    # DOUBLE CHECK THIS
    # for line in text.splitlines():
    #     for word in line.split():
    #         if word != "[REDACTED]":
    #             total_words += 1

    # count over redacts and keep them in a counter
    for line in text.splitlines():
        # right now, over_redact == total number of '[REDACTED]'
        over_redact += line.count("[REDACTED]")

    # for tag in tags:
    #     tag_text = tag.get('text')
    #     tag_text = tag_text.split()
    #     for tag in tag_text:
    #         tags_global.append(tag)
    # under redact simple counter

    # NEW: (Changed the under_redact count to count each phi individually by length of phi)
    for tag in tags:
        tag_type = tag.get('TYPE')
        tag_text = tag.get('text')
        if text.find(tag_text) != -1:
            # this adjustment should count each word instead of each phi
            under_redact += len(tag_text.split())

    # Old:
    # for tag in tags:
    #     tag_type = tag.get('TYPE')
    #     tag_text = tag.get('text')
    #     if text.find(tag_text) != -1:
    #         under_redact += 1
            # Uncomment to dump false negatives types
            # with open("updating_false_neg.txt", "a") as f:
            #     f.write(str(tag_type) + ": " + str(tag_text) + " \n")
            #     #can just comment this out when done dumping files

    # count under redacts and keep them in a dictionary
    for tag in tags:
        tag_type = tag.get('TYPE')
        tag_text = tag.get('text')
        # count total number redacts by type
        if tag_type in type_numbers:
            type_numbers[tag_type] += 1
        else:
            type_numbers[tag_type] = 1

        if text.find(tag_text) == -1:  # phi successfully redacted
            continue
        else:  # phi not redacted
            # add errors to list
            if tag_type in errors:
                errors[tag_type] += [tag_text]
            else:
                errors[tag_type] = [tag_text]

            # add to global counter for errors
            if tag_type in error_numbers:
                error_numbers[tag_type] += 1
            else:
                error_numbers[tag_type] = 1
            # under_redact += 1 --> now done above

    # over redact: = count of [redacted] in text - correct redacts (which is expected number of redacts - missed redacts)
    over_redact = over_redact - (total_redact - under_redact)
    # avoids negative calculations that occasionally result
    over_redact = max(over_redact, 0)
    # confusion matrix calculations
    false_neg = under_redact
    false_pos = over_redact
    true_pos = total_redact - under_redact
    # NEW --> changed this to take the total words and subract the true positives (i think its right but if not its really close)
    # should be total words - (false neg (any left over PHI) + true pos + false pos (any instance of redacted))
    true_neg = total_words - (false_neg + true_pos + false_pos)

    #could also print total words

    # Figure out if file should be looking at xml or text or both for metrics

    precision, recall, f1, neg_predecitive_val = metrics_calc_new(
        false_neg, false_pos, true_neg, true_pos)

    print("File: " + gpt_path.split('/')[-1])
    print("False negatives: ", false_neg)
    print("True negatives: ", true_neg)
    print("False positives: ", false_pos)
    print("True positives: ", true_pos)
    print("Precision: ", precision)
    print("Recall: ", recall)
    print("F1: ", f1)
    print("NPV: ", neg_predecitive_val)
    print("List of Errors: " + str(errors))
    print("---")

    return false_neg, false_pos, true_neg, true_pos, total_redact


def metrics_calc_new(false_neg, false_pos, true_neg, true_pos):
    precision = true_pos / (true_pos + false_pos)
    recall = true_pos / (true_pos + false_neg)
    f1 = 2 * (precision * recall) / (precision + recall)
    neg_predecitive_val = true_neg / (true_neg + false_neg)

    return precision, recall, f1, neg_predecitive_val


def calc_type_accuracy():
    type_accuracy = {}
    false_neg_per_cat = {}
    true_neg_per_type = {}
    npv_per_type = {}
    true_pos_per_type = {}
    recall_by_type = {}

    # error_numbers[type]: count of errors of specific type
    # type_numbers[type] total count of that type in the ground truth.

    for type in type_numbers.keys():
        # *general accuracy: 1 - errors/total_tags_per_type

        type_accuracy[type] = 1 - \
            (error_numbers.get(type, 0) / type_numbers[type])

        false_neg_per_type = type_numbers[type] - error_numbers.get(type, 0)
        false_neg_per_cat[type] = type_numbers[type] - false_neg_per_type

        # true_neg_per_type[type] = false_neg_per_type

        # true_pos_per_type[type] = type_numbers[type] - false_neg_per_cat[type]

        # Calculate true negatives for each type
        true_pos_per_type[type] = type_numbers[type] - false_neg_per_cat[type]

        # Calculate true positives for each type
        # true_neg_per_type[type] = type_numbers[type] - false_neg_per_cat[type]

        # npv_per_type[type] = true_neg_per_type[type] / \
        #     (true_neg_per_type[type] + false_neg_per_cat[type])

        recall_by_type[type] = true_pos_per_type[type] / \
            (true_pos_per_type[type]+false_neg_per_cat[type])

        # true_pos: total number of tags for a type - number under redacts for a type

    return type_accuracy, false_neg_per_cat, true_neg_per_type, true_pos_per_type, npv_per_type, recall_by_type


if __name__ == "__main__":
    gpt_redact = iterate_dir(
        'test_head2head')  # this is results from gpt_redact that you are analyzing
    answers = []
    for file in gpt_redact:
        # print(file)
        # this is the gound truth values (with / at the end)
        ans = 'ground_truth/testing-PHI-Gold-fixed/' + \
            file.split('/')[-1].split('.')[0] + '.xml'
        answers.append(ans)

    print("----------------------------\n\n")
    print("ERROR ANALYSIS\n\n")
    print("----------------------------\n\n")

    # loop through directories and compare files
    for (gpt, ans) in zip(gpt_redact, answers):
        # make sure folders are aligned by name
        if gpt.split('/')[-1].split('.')[0] != ans.split('/')[-1].split('.')[0]:
            print("FILES NOT ALIGNED: CHECK GPT AND ANSWERS FOLDER ORDER")
            break

        # mistakes, under_redacts, over_redacts = compare(gpt, ans)

        false_neg, false_pos, true_neg, true_pos, total_redact = compare(
            gpt, ans)
        tot_false_neg += false_neg
        tot_false_pos += false_pos
        tot_true_neg += true_neg
        tot_true_pos += true_pos

    # calculate accuracy breakdown by type:
    type_accuracy, false_neg_per_cat, true_neg_per_type, true_pos_per_type, npv_per_type, recall_per_type = calc_type_accuracy()
    precision, recall, f1, neg_predecitive_val = metrics_calc_new(
        tot_false_neg, tot_false_pos, tot_true_neg, tot_true_pos)

    print("------------------------------------------------------------\n\n")
    print("OVERALL RESULTS\n\n")
    print("Number of Files Analyzed: " + str(len(gpt_redact)))
    print("\n")
    print("Total Number of False Positives: " + str(tot_false_pos))
    print("Total Number of False Negatives: " + str(tot_false_neg))
    print("Total Number of True Positives: " + str(tot_true_pos))
    print("Total Number of True Negatives: " + str(tot_true_neg))
    print("\n")
    print("Precision: ", precision)
    print("Recall: ", recall)
    print("F1: ", f1)
    print("NPV: ", neg_predecitive_val)
    print("\n")
    print("Recall Breakdown by Error Type: " + str(recall_per_type) + "\n")
    # print("True Negatives by Error Type: " + str(true_neg_per_type) + "\n")
    print("True Positives by Error Type: " + str(true_pos_per_type) + "\n")
    print("False Negatives by Error Type: " + str(false_neg_per_cat) + "\n")
    # print("NPV by Error Type: " + str(npv_per_type) + "\n\n")

    # precision breakdown by error type
    # f1 breakdown by error type
    # npv breakdown by error type
    # ^^ if possible
