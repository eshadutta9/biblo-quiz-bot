#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 25 21:00:56 2023

@author: arnobchowdhury
"""
import os
import pinecone


import time

index_name = 'bot-short-term-memory'
pinecone.init(
    api_key=os.environ.get('pinecone_short_term_mem'),
    environment="gcp-starter",
)
if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        index_name,
        dimension=384,
        metric='cosine'
    )
    # wait for index to finish initialization
    while not pinecone.describe_index(index_name).status['ready']:
        time.sleep(1)

index = pinecone.Index(index_name)


# %% Short Term Memory Retrieval
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')
import uuid

def find_recent_conversation(user_input):
    # Use Pinecone to search for recent conversations
    # (Assuming user_input_embeddings is the embedding of the user's input)
    results = pinecone.index(index_name).query(queries=[user_input_embeddings])

    if results:
        # Retrieve and return the context and responses from the top result
        context, responses = results[0].metadata["context"], results[0].metadata["responses"]
        return context, responses
    else:
        return None, None
def insert_user_conversation_in_stm(user_input, index):

    user_embed = model.encode("Can you expalain me anything about cars").tolist()
    unique_id = str(uuid.uuid4())
    metadata = {"context": "some context", "timestamp": "2023-01-01"}
    index.upsert([(unique_id, user_embed, metadata)])

def delete_bot_stm(index):
    index.delete(delete_all=True, namespace='example-namespace')

def delete_partial_stm(index):
    index.delete(
        ids=['301bca65-d2d2-4b43-aa1b-97d75d206141']
    )
   
#insert_user_conversation_in_stm("Hey I want to learn about physics, help me please", index)
delete_partial_stm(index)