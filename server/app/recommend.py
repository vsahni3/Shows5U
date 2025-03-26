import cohere
import os 
from dotenv import load_dotenv
import numpy as np
from app.crud import *
from app.models import UserRecommendation
from pinecone import Pinecone, ServerlessSpec
from app.utils import to_ascii_safe_id
load_dotenv()
# can later build model like transformer, takes in preferenes + ratings and current title and gives score
# for training we use titles which also have user ranking associated to eval score
# Initialize Cohere client


# KEYWORDS FOR COMMENTS + GENRES
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
            "id": f"{content_types[i]}_{to_ascii_safe_id(titles[i])}",
            "values": embeddings[i]
        }
        for i in range(len(embeddings))
    ]

    pc_index.upsert(vectors=vectors)



def keyword_match_boost(pref_comments, rec_texts, boost=0.2):
    """
    Simple keyword boost based on exact word matching.
    Returns a boost factor array (R,) for recommendations.
    """
    boost_scores = np.zeros(len(rec_texts))
    
    for comment in pref_comments:
        if comment.strip():
            pattern = re.compile(r'\b{}\b'.format(re.escape(comment.strip())), re.IGNORECASE)
            matches = [len(pattern.findall(text)) for text in rec_texts]
            boost_scores += np.array(matches, dtype=float)
    
    # Clip boost scores (max 1 for multiple matches)
    boost_scores = np.clip(boost_scores, 0, 1)
    
    return boost_scores * boost


def retrieve_embeddings(items: list[tuple[str, str]]):
    if not items:
        return []
    ids = [f"{content_type}_{to_ascii_safe_id(title)}" for title, content_type in items]
    response = pc_index.fetch(ids=ids)
    embeddings = [response.vectors[item_id].values for item_id in ids]
    assert len(embeddings) == len(ids)
    return embeddings


def genre_match(preferences: list, recommendations: list):
    # normalize by dividing by preference len (not rec len)
    # if rec has 10 genres, pref has 2 and 2 mathes, score should be 1 rather than 0.2
    scores = np.full((len(preferences), len(recommendations)), -1)
    score_sum = 0
    score_count = 0
    for i in range(len(preferences)):
        pref_genres = preferences[i].genres.split(', ')
        for j in range(len(recommendations)):
            rec_genres = recommendations[j]['genres']
            if pref_genres and rec_genres:
                scores[i][j] = len(set(pref_genres).intersection(set(rec_genres))) / len(pref_genres)
                score_sum += scores[i][j]
                score_count += 1
    score_mean = score_sum / score_count if score_count > 0 else 0
    scores[scores == -1] = score_mean
    return scores


def embed_match(pref_embeddings: list[list[float]], rec_embeddings: list[list[float]]):


    pref_embeddings = np.array(pref_embeddings) # (P, D) -> Preferences
    rec_embeddings = np.array(rec_embeddings) # (R, D) -> Recommendations
    
    dot_products = np.dot(pref_embeddings, rec_embeddings.T)  # (P, R)

    pref_norms = np.linalg.norm(pref_embeddings, axis=1, keepdims=True)  # (P, 1)
    rec_norms = np.linalg.norm(rec_embeddings, axis=1)  # (R,)
    
    cosine_similarity = dot_products / (pref_norms * rec_norms.T)  # (P, R)
    normalized_cs = (cosine_similarity + 1) / 2
    return normalized_cs 

def add_ranks(scores: np.array, ratings: list[int], alpha: float = 0.75):
    # scores is (p, r)
    # Normalize ranks to [0,1] range
    
    min_rank, max_rank = 1, 5
    normalized_ratings = (ratings - min_rank) / (max_rank - min_rank)  # (P,)

    scores_with_rating = (
        normalized_ratings[:, None] * (alpha * scores + (1 - alpha)) +
        (1 - normalized_ratings[:, None]) * (alpha * (1 - scores))
    )  # (P, R)

    final_scores = np.mean(scores_with_rating, axis=0)  
    return final_scores 

def rank_recommendations(preferences: list, recommendations: list, k: int = 20):

    if not preferences:
        length = min(len(recommendations), k)
        return list(range(length)), [50] * length
    pref_ratings = np.array([row.rating for row in preferences])
    # both scores betwee 0 and 1
    genre_scores = genre_match(preferences, recommendations)
    genre_scores_with_ratings = add_ranks(genre_scores, pref_ratings)

    pref_embeddings = retrieve_embeddings(items=[(row.title, row.content_type) for row in preferences])

    rec_descriptions = [rec['description'] for rec in recommendations]
    rec_embeddings = get_embeddings(rec_descriptions)
    
    embed_scores = embed_match(pref_embeddings, rec_embeddings)
    embed_scores_with_ratings = add_ranks(embed_scores, pref_ratings)

    scores = (genre_scores_with_ratings + embed_scores_with_ratings) / 2
    
    top_k_indices = np.argsort(scores)[::-1][:k]
    top_k_scores = scores[top_k_indices]  
    
    return top_k_indices, top_k_scores


def give_recommendations(recommendations: list, user_id: str, content_type: str, k: int = 20):
    preferences = get_user_recommendations(user_id, content_type, cols=(UserRecommendation.title, UserRecommendation.rating, UserRecommendation.content_type, UserRecommendation.seen))
    seen = {row.title for row in preferences if row.seen}
    unseen_recommendations = [rec for rec in recommendations if rec['title'] not in seen]
    top_k_indices, top_k_scores = rank_recommendations(preferences, unseen_recommendations, k)
    norm_scores = top_k_scores * 100

    final_recs = [unseen_recommendations[index] | {"score": norm_scores[i]} for i, index in enumerate(top_k_indices)]
    return final_recs
    

def delete_pinecone(pc_index):
    pc_index.delete(delete_all=True)
    
if __name__ == "__main__":
    pass
    # all isekai
    # pref1 = "Subaru Natsuki, an ordinary high school student, is suddenly transported to a fantasy world. Without any special powers, he discovers he has the ability to return from death, resetting time upon each demise. Determined to protect his newfound friends and uncover the mysteries of this world, Subaru faces relentless challenges and perilous foes."
    # pref1 = "badass"
    # pref2 = "Satoru Mikami, a 37-year-old corporate worker, is reincarnated into a fantasy realm as a slime—a low-level monster. Possessing unique abilities, he befriends various creatures and embarks on a journey to create a world where all races can coexist peacefully."
    # pref3 = "In the year 2022, thousands of players find themselves trapped in 'Sword Art Online,' a virtual reality MMORPG, where death in the game means death in real life. Protagonist Kirito must navigate this perilous world, battling foes and forming alliances, to find a way back to reality."

    # # Recommendations: Isekai, Shounen, and Shoujo Anime Descriptions
    # rec1 = "Momonga, a devoted player of the MMORPG Yggdrasil, finds himself unable to log out as the game's servers shut down. Transformed into his in-game character—a powerful skeletal overlord—he sets out to explore this new reality, seeking answers and asserting his dominance over the land."
    # rec1 = pref2
    # rec2 = "In a world where superpowers, known as 'Quirks,' are the norm, Izuku Midoriya dreams of becoming a hero despite his lack of powers. His life changes when he inherits the Quirk of the world's greatest hero, embarking on a journey to become the symbol of peace."
    # rec3 = "After a family tragedy leaves her homeless, high school student Tohru Honda moves in with the mysterious Sohma family. She soon discovers they are cursed to transform into animals of the Chinese zodiac when hugged by the opposite sex, leading to heartfelt and comedic moments as she becomes entwined in their lives."

    # # Generate embeddings for preferences and recommendations
    # prefs = get_embeddings([pref1, pref2, pref3])
    # recs = get_embeddings([rec1, rec2, rec3])

    # # Example ratings for preferences
    # ratings = [5, 5, 5]

    # # Rank recommendations
    # ranked_recs = rank_recommendations(prefs, ratings, recs)
    # print(ranked_recs)
    pc_index = create_pinecone_index()
    print(pc_index.describe_index_stats())

    

    

    