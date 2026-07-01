from difflib import SequenceMatcher


def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_best_match(ocr_text, medicines):

    best_score = 0
    best_medicine = None

    ocr_text = ocr_text.lower()

    for medicine in medicines.find():

        name = medicine["Generic Name"]

        score = similarity(name, ocr_text)

        # Also compare first word
        first_word = name.split()[0]

        score = max(
            score,
            similarity(first_word, ocr_text)
        )

        if first_word.lower() in ocr_text:
            score = 1.0

        if score > best_score:
            best_score = score
            best_medicine = medicine

    return best_medicine, best_score