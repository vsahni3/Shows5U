import cohere
import os 
from dotenv import load_dotenv
import chromadb
import numpy as np
from chromadb.config import Settings
load_dotenv()
# can later build model like transformer, takes in preferenes + ratings and current title and gives score
# for training we use titles which also have user ranking associated to eval score
# Initialize Cohere client
co = cohere.Client(os.getenv('COHERE_API_KEY'))
client = chromadb.Client(Settings())
collection = client.create_collection(name='embeddings')
def get_embedding(description):
    response = co.embed(
        texts=[description],
        model='embed-english-v2.0',
        truncate='END'
    )
    return response.embeddings[0]

def store_embedding(content_type, title, description):
    embedding = get_embedding(description)

    unique_id = f"{content_type}_{title}"

    collection.add(
        ids=[unique_id],
        embeddings=[embedding],
        metadatas=[{'content_type': content_type, 'title': title, 'description': description}]
    )




def compute_score(embedding1, embedding2, rank, alpha=0.75):

    embedding1 = np.array(embedding1)
    embedding2 = np.array(embedding2)
    
  
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    cosine_similarity = dot_product / (norm1 * norm2)
    

    min_rank = 1
    max_rank = 5
    normalized_rank = (rank - min_rank) / (max_rank - min_rank)
    
    score = normalized_rank * (alpha * cosine_similarity + (1 - alpha)) + (1 - normalized_rank) * (alpha * (1 - cosine_similarity))
    
    return score



def rank_recommendations(preferences, recommendation_embeddings, k=5, alpha=0.75):


    pref_embeddings = np.array([pref[0] for pref in preferences])  # (P, D) -> Preferences
    pref_ranks = np.array([pref[1] for pref in preferences])       # (P,)   -> Ranks
    rec_embeddings = np.array(recommendation_embeddings)           # (R, D) -> Recommendations
    
    dot_products = np.dot(pref_embeddings, rec_embeddings.T)  # (P, R)
    pref_norms = np.linalg.norm(pref_embeddings, axis=1, keepdims=True)  # (P, 1)
    rec_norms = np.linalg.norm(rec_embeddings, axis=1)  # (R,)
    
    cosine_similarity = dot_products / (pref_norms * rec_norms.T)  # (P, R)
    normalized_cs = (cosine_similarity + 1) / 2
    # Normalize ranks to [0,1] range
    min_rank, max_rank = 1, 5
    normalized_ranks = (pref_ranks - min_rank) / (max_rank - min_rank)  # (P,)

    scores_per_pref = (
        normalized_ranks[:, None] * (alpha * normalized_cs + (1 - alpha)) +
        (1 - normalized_ranks[:, None]) * (alpha * (1 - normalized_cs))
    )  # (P, R)

    final_scores = np.mean(scores_per_pref, axis=0)  # (R,)

    top_k_indices = np.argsort(final_scores)[::-1][:k]
    top_k_scores = final_scores[top_k_indices]

    return list(zip(top_k_indices, top_k_scores))


