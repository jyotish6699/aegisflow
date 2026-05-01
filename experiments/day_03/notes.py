intent_freq = {
    "help": 4,
    "confidence": 8,
    "roadmap": 9
}

key = max(intent_freq)
# output = key of max alphabetically 

iterate = "list", "dict"
# dominant_intent = max(iterate, key=function)
# call that function of every iteration 
dominant_intent = max(intent_freq, key=intent_freq.get)
# in this dominant_intent max function i call get function so it has no paranthesis 
# whenever you call any function inside any function then not paranthesis 
# paranthesis pass when you want to execute that function on that time 
# output = key of max value

words = ["apple", "banana", "kiwi"]
max_len = max(words, key=len)
# output = return string, max len of string 


