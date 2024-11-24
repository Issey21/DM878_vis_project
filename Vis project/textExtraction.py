import re

def extract(path):
    re_parenthesis = re.compile("[\(\[\{].*?[\}\]\)]")  # matches on all parenthesis and everything inside of them
    re_puntuation = re.compile("[\.\,;!?\"\-'’”…]")    # matches on punctuation except ":"
    re_names = re.compile(".*:")

    speakers = {""}  # set of all speakers
    currentSpeaker = "" # the current speaker for the current part of the transcript
    words = [""]    # all words in the transcript. Each index is a word, in the order they come in the transcript
    speaker = [""]  # the speaker for the word on the same index in "words"

    with open(path, 'r', encoding="utf-8") as file:
        for line in file:
            l = line

            # Cleans each line in the file by removing unnecessary characters and text 
            l = re.sub(re_parenthesis, "", l).strip()
            l = re.sub(re_puntuation, "", l).strip()

            # Extracts name of the speaker for this line, if the line has a speaker.
            # If no speaker is mentioned, it is assumed the previously mentioned speaker, is the speaker
            # for this line as well.
            lineSpeaker = re.match(re_names, l)
            if lineSpeaker:
                currentSpeaker = re.sub(":", "", lineSpeaker.group(0)).strip()
                speakers.add(currentSpeaker)
                l = re.sub(lineSpeaker.group(0), "", l).strip()  # removes the name of the speaker from the line

            l = l.casefold().split()    # Splits the line into seperate words
            words.extend(l) # appends the words to the list of all words

            for word in l:  # assigns a speaker to each word in l
                speaker.append(currentSpeaker)

    # if no element is added to the set, Python does not see it as a set, so the empty elements need to be removed...
    speakers.remove("") 
    words.remove("")
    speaker.remove("")

    return [speakers, words, speaker]