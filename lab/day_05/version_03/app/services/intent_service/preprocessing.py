def preprocess(text: str):
    message = text.lower()

    tokens = message.split()
    
    return message, tokens


# message, tokens = preprocess("i need help")
# print(message)
# print(tokens)