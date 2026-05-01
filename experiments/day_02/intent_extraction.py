def intent_extraction(text: str) -> list[str]:

    INTENT_RULES = {
    "help": ['help', 'assist', 'support', 'confused'],
    "motivation": ['motivation', 'inspire', 'encourage'],
    "guidance": ['guidance', 'guide', 'mentor'],
    "roadmap": ['roadmap', 'plan', 'steps', 'path']
    }

    message = text.lower()
    detected_intents = []
    for intent, patterns in INTENT_RULES.items():
        if any(p in message for p in patterns):
            #print(p) i can print 'p' outside any() function because function is a scope level, so outside can't access variable.
            detected_intents.append(intent)

    if not detected_intents:
        detected_intents.append("unknown")

    return detected_intents
        

a = intent_extraction("i need help i am confused motivation")
print(a)


# 2nd method expansion
# def intent_detection(text:str) -> list[str]:
#     message = text.lower()
#     detected_intents = []
#     for intent, patterns in INTENT_RULES.items():
#         for p in patterns:
#             if p in message:
#                 detected_intents.append(p)

#     return detected_intents

# b=intent_detection("i am motivation help")
# print(b)