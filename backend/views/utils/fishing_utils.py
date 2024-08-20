from flask import current_app
from backend import mail
from backend.models import Parter, User, FishingMessages
from flask_mail import Message
import numpy as np
import json
import faiss
from sentence_transformers import SentenceTransformer
from transformers import AutoModel, AutoTokenizer
import torch.nn.functional as F
from torch import Tensor
import numpy as np
from backend.views.utils.chat_preprocess import ChatProcessor

embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
speech_sim_model = AutoModel.from_pretrained('dbtmddn41/speech_tone')
speech_sim_tokenizer = AutoTokenizer.from_pretrained("llmrails/ember-v1")

def preprocess_partner_msg(msg):
    pass



def average_pool(last_hidden_states: Tensor,
                 attention_mask: Tensor) -> Tensor:
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

def calc_sim(anchor, txt):
    anchor_inputs = speech_sim_tokenizer(anchor, return_tensors="pt", padding=True, truncation=True).to(speech_sim_model.device)
    txt_inputs = speech_sim_tokenizer(txt, return_tensors="pt", padding=True, truncation=True).to(speech_sim_model.device)

    anchor_output = speech_sim_model(**anchor_inputs)
    txt_output = speech_sim_model(**txt_inputs)
    anchor_embeddings = average_pool(anchor_output.last_hidden_state, anchor_inputs['attention_mask'])
    anchor_embeddings = F.normalize(anchor_embeddings, p=2, dim=1)
    txt_embeddings = average_pool(txt_output.last_hidden_state, txt_inputs['attention_mask'])
    txt_embeddings = F.normalize(txt_embeddings, p=2, dim=1)
    return (anchor_embeddings @ txt_embeddings.T).item()

def get_speech_similarity(msg, origin_msg):
    return calc_sim(origin_msg, msg)

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