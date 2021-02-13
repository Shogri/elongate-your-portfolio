import string
import nltk

tweet = "Star Light, Star Bright" 

tweet_token = nltk.word_tokenize(tweet)
tagged_tokens = nltk.pos_tag(tweet_token)

#check to see if tweet is longer than 1 word
if (len(tagged_tokens) > 1):
    tagged_tokens = tagged_tokens[1:]

for w in tagged_tokens:
    if (w[1] == 'NNP'):
        print(w[0])
    