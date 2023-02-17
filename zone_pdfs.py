import pdfplumber
import re

def read_pdf_text(filepath, filename, pages_to_ignore, question_data, removal_lines_starting):
    try:
        raw_text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                if page.page_number not in pages_to_ignore:
                    page_text = page.extract_text(x_tolerance=1)
                    # Split on new line character and get rid of any \r should they surface
                    page_text_array = page_text.replace("\r", "").split("\n")
                    for i in range(0, len(page_text_array) - 1):
                        # Ignore lines starting with anything in the supplied list and blank lines
                        if (
                            not page_text_array[i].startswith(
                                tuple(removal_lines_starting)
                            )
                            and page_text_array[i] != ""
                        ):
                            raw_text += page_text_array[i].strip() + "\n"
                            # Condensing white space to single spacing

        # raw_text = " ".join(raw_text.split())

        # Now I have the block answer split into question areas using question_data
        # Questions MUST be ordered in question data else this falls apart
        # Logic picks up first question_data, finds where the word block starts and reads until it hits the next block from the next question
        # If this is the last question block read until the end of the text

        question_blocks = []
        question_processed_text = raw_text

        for i, question in enumerate(question_data):
            if i < len(question_data) - 1:
                for question_text_start in question_data[i]["question_text_start"]:
                    question_search = re.search(
                        question_text_start, question_processed_text, re.IGNORECASE
                    )
                    if question_search is not None:
                        break
                if question_search is None:
                    # Better to have all of the answers in one block instead of no answers
                    current_q_index = len(question_processed_text)
                    print(
                        f"Filename {filename} could not find current question for question i:{i}"
                    )
                else:
                    current_q_index = question_search.span()[0]

                for question_text_start in question_data[i + 1]["question_text_start"]:
                    question_search = re.search(
                        question_text_start, question_processed_text, re.IGNORECASE
                    )
                    if question_search is not None:
                        break
                if question_search is None:
                    # Better to have all of the answers in one block instead of no answers
                    next_q_index = len(question_processed_text)
                    print(
                        f"Filename {filename} could not find next question for question i:{i}"
                    )
                else:
                    next_q_index = question_search.span()[0]

                response = question_processed_text[current_q_index:next_q_index]
                question_processed_text = question_processed_text[
                    next_q_index : len(question_processed_text)
                ]
            elif i == len(question_data) - 1:
                # If it's the last question assume the rest of the doc is the response
                response = question_processed_text[0 : len(question_processed_text)]
            question_blocks.append(
                {"question_title": question["question_title"], "response": response}
            )
    except Exception as e:
        print(e)
        print(filename)
    return question_blocks

question_data = [{"question_title": "QUESTION_1", "question_text_start": ["QUESTION 1\nPart a ","QUESTION 1 Part a"]},]

removal_lines_starting = ["DAVE"]