import re   # regular expression

path = "Transcripts/TestScript.txt"
re_date = re.compile("\(\d{2}:\d{2}\)")    # matches timestamps on the format (dd:dd) where d = [0-9]
re_name = re.compile(".+:\s") # matches on speakers. Whenever there is a speaker, their name is stated as "NAME: ".
re_endOfSentence = re.compile(".+\.$")   # matches on end of sentence. 

# Extracting all words
# transcript_words = open(path, "r").read().split()

# # Finds the names of all speakers
# for index, word in enumerate(transcript_words):
#     if(re_name.match(word)):
#         names.append(word)

# # Removing timestamps from text
# for index, word in enumerate(transcript_words):
#     if(re_date.match(word)):
#         transcript_words.pop(index)

line = []
names = []
name = ""

with open(path, 'r') as file:   # reading file

    for l in file:  # reading one line at a time
        name = re.findall(re_name, l)
        if(len(name) > 0):
            names.append(name)




print(f'Names: {names} \n')
# print(transcript_words)