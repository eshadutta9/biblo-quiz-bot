#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 18:58:32 2023

@author: arnobchowdhury
"""
# %% open AI embedding
import requests

api_key = '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'

api_endpoint = "https://api.openai.com/v1/embeddings"

data = {
    "input": "Your text string goes here",
    "model": "text-embedding-ada-002"
}

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Make the API call
response = requests.post(api_endpoint, json=data, headers=headers)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Extract and print the embedding
    embedding = response.json()["embedding"]
    print(embedding)
else:
    # Print an error message if the request was not successful
    print(f"Error: {response.status_code}\n{response.text}")
    
    
#%% Maths Qa dataset
from datasets import load_dataset

dataset = load_dataset("math_qa")
    
# %% Embeding model 1
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')

#Our sentences we like to encode
sentences = ['This framework generates embeddings for each input sentence',
    'Sentences are passed as a list of string containing 2 dog instances',
    'The quick brown fox jumps over the lazy dog.']

#Sentences are encoded by calling model.encode()
embeddings = model.encode(sentences)

#Print the embeddings
for sentence, embedding in zip(sentences, embeddings):
    print("Sentence:", sentence)
    print("Embedding:", embedding)
    print("")

query_embedding = model.encode('What does dog do?')

print("Similarity:", util.dot_score(query_embedding, embeddings))

# %% Embedding Model 2
model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

query_embedding = model.encode('What does fox do?')
passage_embedding = model.encode(['The fox ran after dog barked at it',
    'the dog bit fox',
    'The quick brown fox jumps over the lazy dog.'])

print("Similarity:", util.dot_score(query_embedding, passage_embedding)) 


# %% TEST Flan Model Text to Text

import requests

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-xxl"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

# Demo Previous Knowledge
llmchain_information = [
    'BOT: What was the gender of the dog? user: The dog was a female',
    'BOT: How did you feel? user: I felt scared',
    'BOT: What was your impression of it? user: This was so cool',
    'BOT: Where were you going? user: I was going to school',
    'BOT: What did you have to do later? user: I have to come back then',
]
knowledge = "\n".join(llmchain_information)
augmented_prompt = 'Using the contexts above.'
query2 = "do you remember where I was going?"

inputs = knowledge + " " + augmented_prompt + " " + query2 

output = query({
	"inputs": inputs,
})
print(output)



# %%
import requests
from datasets import load_dataset
from sentence_transformers import SentenceTransformer, util

def openai_embedding(api_key, text, model="text-embedding-ada-002"):
    api_endpoint = "https://api.openai.com/v1/embeddings"

    data = {
        "input": text,
        "model": model
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(api_endpoint, json=data, headers=headers)

    if response.status_code == 200:
        return response.json()["embedding"]
    else:
        print(f"Error: {response.status_code}\n{response.text}")
        return None

def load_math_qa_dataset():
    dataset = load_dataset("math_qa")
    return dataset

def sentence_transformer_embedding(model_name, sentences):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(sentences)
    
    for sentence, embedding in zip(sentences, embeddings):
        print("Sentence:", sentence)
        print("Embedding:", embedding)
        print("")

    return embeddings

def calculate_similarity(query_embedding, passage_embeddings):
    return util.dot_score(query_embedding, passage_embeddings)

def flan_model_text_to_text(api_url, headers, payload):
    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()

# Example usage:

# OpenAI Embedding
openai_api_key = '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'
openai_text = 'Ask me anything'
openai_result = openai_embedding(openai_api_key, openai_text)
print(openai_result)

# Load Math QA Dataset
math_qa_dataset = load_math_qa_dataset()
print(math_qa_dataset)

# Sentence Transformer Embedding
sentences_to_embed = ['This is sentence 1', 'This is sentence 2', 'This is sentence 3']
sentence_transformer_model = 'all-MiniLM-L6-v2'
sentence_transformer_result = sentence_transformer_embedding(sentence_transformer_model, sentences_to_embed)

# Calculate Similarity
query_emb = sentence_transformer_result[0]
passage_embs = sentence_transformer_result[1:]
similarity_score = calculate_similarity(query_emb, passage_embs)
print("Similarity Score:", similarity_score)

# Flan Model Text to Text
flan_api_url = "https://api-inference.huggingface.co/models/google/flan-t5-xxl"
flan_headers = {"Authorization": "Bearer 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"}
flan_payload = {"inputs": "Your input text here"}
flan_result = flan_model_text_to_text(flan_api_url, flan_headers, flan_payload)
print(flan_result)

