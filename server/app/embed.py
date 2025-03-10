import cohere
import os 
from dotenv import load_dotenv
import chromadb
import numpy as np
from crud import *
from app.models import UserRecommendation
from chromadb.config import Settings
load_dotenv()
# can later build model like transformer, takes in preferenes + ratings and current title and gives score
# for training we use titles which also have user ranking associated to eval score
# Initialize Cohere client
co = cohere.Client(os.getenv('COHERE_API_KEY'))
client = chromadb.Client(Settings())
collection = client.create_collection(name='embeddings')
def get_embeddings(descriptions):
    response = co.embed(
        texts=[descriptions],
        model='embed-english-v2.0',
        truncate='END'
    )
    return response.embeddings[0]

def store_embeddings(content_types: list[str], titles: list[str], descriptions: list[str]):

    embeddings = get_embeddings(descriptions)
    vectors = []

    vectors = [
        {
            "id": f"{content_types[i]}_{titles[i]}",
            "values": embeddings[i]
        }
        for i in range(len(embeddings))
    ]
    collection.upsert(vectors=vectors)


def retrieve_embeddings(items: list[tuple[str, str]]):
    """
    Retrieves embeddings for a given list of (title, content_type) tuples in the same order.

    :param items: List of tuples (title, content_type).
    :return: List of embeddings corresponding to the input order. Returns None if an embedding is not found.
    """
    ids = [f"{content_type}_{title}" for title, content_type in items]
    
    results = collection.fetch(ids=ids)

    embeddings = [results.get(item_id, {}).get("values", None) for item_id in ids]
    
    return embeddings



def rank_recommendations(pref_embeddings: list[list[float]], pref_ratings: list[int], rec_embeddings: list[list[float]], k: int = 5, alpha: float = 0.75):


    pref_embeddings = np.array(pref_embeddings) # (P, D) -> Preferences
    pref_ratings = np.array(pref_ratings) # (P,)   -> Ranks
    rec_embeddings = np.array(rec_embeddings) # (R, D) -> Recommendations
    
    dot_products = np.dot(pref_embeddings, rec_embeddings.T)  # (P, R)
    pref_norms = np.linalg.norm(pref_embeddings, axis=1, keepdims=True)  # (P, 1)
    rec_norms = np.linalg.norm(rec_embeddings, axis=1)  # (R,)
    
    cosine_similarity = dot_products / (pref_norms * rec_norms.T)  # (P, R)
    normalized_cs = (cosine_similarity + 1) / 2
    # Normalize ranks to [0,1] range
    min_rank, max_rank = 1, 5
    normalized_ranks = (pref_ratings - min_rank) / (max_rank - min_rank)  # (P,)

    scores_per_pref = (
        normalized_ranks[:, None] * (alpha * normalized_cs + (1 - alpha)) +
        (1 - normalized_ranks[:, None]) * (alpha * (1 - normalized_cs))
    )  # (P, R)

    final_scores = np.mean(scores_per_pref, axis=0)  # (R,)

    top_k_indices = np.argsort(final_scores)[::-1][:k]
    top_k_scores = final_scores[top_k_indices]

    return list(zip(top_k_indices, top_k_scores))


def give_recommendations(rec_descriptions: list[str], user_id: str, k: int = 5):
    preferences = get_user_recommendations(user_id, cols=(UserRecommendation.title, UserRecommendation.rating, UserRecommendation.content_type))
    pref_ratings = [row.rating for row in preferences]
    pref_embeddings = retrieve_embeddings(items=[(row.title, row.content_type) for row in preferences])

    rec_embeddings = get_embeddings(rec_descriptions)
    return rank_recommendations(pref_embeddings, pref_ratings, rec_embeddings, k)

    
    
    