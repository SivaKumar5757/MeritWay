from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load pre-trained model and tokenizer
model_name = 'gpt2'
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Define conversation history and context
conversation_history = []

# Function to generate response
def chat_with_gpt2(user_input):
    # Append user input to conversation history
    conversation_history.append(user_input)
    
    # Encode the new user input, add the end-of-text token, and return a tensor in Pytorch
    input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')
    
    # Generate a response using the model
    response = model.generate(input_ids, max_length=100, num_return_sequences=1, no_repeat_ngram_size=2, eos_token_id=tokenizer.eos_token_id)
    
    # Decode and format the response
    chatbot_response = tokenizer.decode(response[0], skip_special_tokens=True)
    
    return chatbot_response

# Main interaction loop
print("Welcome to the GPT-2 Chatbot. Enter 'exit' to end the conversation.")
while True:
    user_input = input("You: ")
    
    if user_input.lower() == 'exit':
        print("Chatbot: Goodbye!")
        break
    
    # Get GPT-2 response
    gpt2_response = chat_with_gpt2(user_input)
    
    print("Chatbot:", gpt2_response)
