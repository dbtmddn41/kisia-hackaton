from flask import current_app
from backend import mail
from backend.models import Parter, User, FishingMessages
from flask_mail import Message
import numpy as np
import json
import faiss
from sentence_transformers import SentenceTransformer
embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

def preprocess_partner_msg(msg):
    pass

def get_speech_similarity(msg, user_id):
    user = User.query.get_or_404(user_id)
    return 0.8      #임시값

def get_content_score(msg):
    return 0.6

def get_similar_fishing_msg(msg):
    return search_similar_msgs(msg)

def search_similar_msgs(query, top_k=3):
    fising_messages = FishingMessages.query.all()
    

    vectors = []
    texts = []
    for msg in fising_messages:
        if msg.messge_embedding is None:
            continue
        messge_embedding = np.array(list(map(float, msg.messge_embedding))).astype('float32')
        vectors.append(messge_embedding)
        texts.append(msg.message)

    if not vectors:
        print('no chat vectors')
        return

    # FAISS 인덱스 생성
    vectors = np.array(vectors)
    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)

    # 쿼리 텍스트를 벡터로 변환
    query_vector = embedding_model.encode(query)
    query_vector = np.array(query_vector).reshape(1, -1).astype('float32')
    
    # FAISS를 사용하여 유사한 벡터 검색
    print(query_vector.shape, vectors.shape)
    distances, indices = index.search(query_vector, min(top_k, len(vectors)))   # [[0.84129953]] [[0]]
    
    
    return texts[indices[0][0]]
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

def send_mail(email, **kwargs):
    """요약된 대화 내용을 해당 사용자의 Gmail로 전송합니다."""
    with current_app.app_context():
        if 'contents' in kwargs:
            msg = Message(
                kwargs["title"],
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[email],
            )
            msg.body = f"\n{kwargs['contents']}"

            try:
                print('send to',email)
                mail.send(msg)
            except Exception as e:
                print(f"Failed to send email: {e}")