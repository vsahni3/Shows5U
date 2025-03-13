import cohere
import os 
from dotenv import load_dotenv
import numpy as np
from app.crud import *
from scipy.special import softmax
from app.models import UserRecommendation
from pinecone import Pinecone, ServerlessSpec
load_dotenv()
# can later build model like transformer, takes in preferenes + ratings and current title and gives score
# for training we use titles which also have user ranking associated to eval score
# Initialize Cohere client

def create_pinecone_index():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    index_name = 'embeddings'
    embedding_dimension = 4096  

    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=embedding_dimension,
            metric='cosine', 
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
    index = pc.Index(index_name)
    return index

co = cohere.Client(os.getenv('COHERE_API_KEY'))
pc_index = create_pinecone_index()


def get_embeddings(descriptions):
    response = co.embed(
        texts=descriptions,
        model='embed-english-v2.0',
        truncate='END'
    )
    return response.embeddings

def store_embeddings(content_types: list[str], titles: list[str], descriptions: list[str]):
    embeddings = get_embeddings(descriptions)
    vectors = [
        {
            "id": f"{content_types[i]}_{titles[i]}",
            "values": embeddings[i]
        }
        for i in range(len(embeddings))
    ]

    pc_index.upsert(vectors=vectors)




def retrieve_embeddings(items: list[tuple[str, str]]):
    if not items:
        return []
    ids = [f"{content_type}_{title}" for title, content_type in items]
    response = pc_index.fetch(ids=ids)
    embeddings = [response.vectors[item_id].values for item_id in ids]
    assert len(embeddings) == len(ids)
    return embeddings



def rank_recommendations(pref_embeddings: list[list[float]], pref_ratings: list[int], rec_embeddings: list[list[float]], k: int = 10, alpha: float = 0.75):
    # score gets softmaxed anyways
    if not pref_embeddings or not pref_ratings:
        length = min(len(rec_embeddings), k)
        return list(range(length)), [1] * length

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

    return top_k_indices, top_k_scores


def give_recommendations(recommendations: list, user_id: str, k: int = 20):
    preferences = get_user_recommendations(user_id, cols=(UserRecommendation.title, UserRecommendation.rating, UserRecommendation.content_type))
    pref_ratings = [row.rating for row in preferences]
    pref_embeddings = retrieve_embeddings(items=[(row.title, row.content_type) for row in preferences])


    rec_descriptions = [rec['description'] for rec in recommendations]
    rec_embeddings = get_embeddings(rec_descriptions)
    top_k_indices, top_k_scores = rank_recommendations(pref_embeddings, pref_ratings, rec_embeddings, k)
    norm_scores = softmax(top_k_scores) * 100
    final_recs = [recommendations[index] | {"score": norm_scores[i]} for i, index in enumerate(top_k_indices)]
    return final_recs
    

def delete_pinecone(pc_index):
    pc_index.delete(delete_all=True)
    
if __name__ == "__main__":

    pc_index = create_pinecone_index()
    
    print(pc_index.describe_index_stats())

    