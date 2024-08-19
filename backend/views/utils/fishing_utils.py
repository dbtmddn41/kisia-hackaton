from email_validator import validate_email, EmailNotValidError
from backend.models import Parter, User, FishingMessages
import numpy as np
import json
import faiss
from FlagEmbedding import BGEM3FlagModel

embedding_model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

def get_speech_similarity(msg, user_id):
    user = User.query.get_or_404(user_id)
    return 0.8      #임시값

def get_content_score(msg):
    return 0.3

def get_similar_fishing_msg(msg):
    return "선배 탕후루 사먹게 3000만원만 주세요"

def search_similar_chats(query, top_k=5):
    fising_messages = FishingMessages.query.all()
    
    print('search 개수 :', len(results))

    vectors = []
    for msg in fising_messages:
        if msg.messge_embedding is None:
            continue
        messge_embedding = np.array(list(map(float, msg.messge_embedding))).astype('float32')
        vectors.append(messge_embedding)

    if not vectors:
        print('no chat vectors')
        return

    # FAISS 인덱스 생성
    vectors = np.array(vectors)
    dimension = vectors.shape[1]   # 벡터의 차원 : 1024
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)

    # 쿼리 텍스트를 벡터로 변환
    query_vector = embedding_model.encode(query, batch_size=12, max_length=8192)['dense_vecs']
    query_vector = np.array(query_vector).reshape(1, -1).astype('float32')
    
    # FAISS를 사용하여 유사한 벡터 검색
    print(query_vector.shape, vectors.shape)
    distances, indices = index.search(query_vector, min(top_k, len(vectors)))   # [[0.84129953]] [[0]]
    
    results = []
    return indices[0]
    for i, idx in enumerate(indices[0]):
        chat_id = chat_ids[idx]
        distance = distances[0][i]
        if distance > 10:
            continue
        
        chat_info = chat_table.query.filter_by(chat_id=chat_id).first()
        results.append({
            'chat_id': chat_id,
            'distance': distance,
            'summary': chat_info.summary
        })
    return results