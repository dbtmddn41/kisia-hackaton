from flask import current_app
from backend import mail
from backend.models import Parter, User, FishingMessages
from flask_mail import Message
import numpy as np
import json
import faiss
# from sentence_transformers import SentenceTransformer
from transformers import AutoModel, AutoTokenizer
import torch.nn.functional as F
from torch import Tensor
import numpy as np
from backend.views.utils.chat_preprocess import ChatProcessor
import torch
from io import StringIO
from gluonnlp.data import SentencepieceTokenizer
from kobert import get_tokenizer

# embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
speech_sim_model = AutoModel.from_pretrained('dbtmddn41/speech_tone')
speech_sim_tokenizer = AutoTokenizer.from_pretrained("llmrails/ember-v1")
content_model = AutoModel.from_pretrained('naayeeoon/Phishing-Detection-Model-Based-on-Korean-Text-Content')
tok_path = get_tokenizer()
contnet_tokenizer  = SentencepieceTokenizer(tok_path)

def preprocess_partner_msg(msg, user_name, partner_name):
    chat_processor = ChatProcessor(msg, user_name, partner_name)
    chat_processor.load_data()
    chat_processor.process_person_chat()
    print(chat_processor.get_person_chats())
    return '\n'.join(chat_processor.get_person_chats())


def average_pool(last_hidden_states: Tensor,
                 attention_mask: Tensor) -> Tensor:
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

def calc_tone_embedding(text):
    with torch.no_grad():
        inputs = speech_sim_tokenizer(text, return_tensors="pt", padding=True, truncation=True).to(speech_sim_model.device)
        output = speech_sim_model(**inputs)
        embeddings = average_pool(output.last_hidden_state, inputs['attention_mask'])
        embeddings = F.normalize(embeddings, p=2, dim=1)
    return embeddings


def get_speech_similarity(msg, origin_msg):
    origin_embeddings = calc_tone_embedding(origin_msg)
    msg_embeddings = calc_tone_embedding(msg)
    sim = (origin_embeddings @ msg_embeddings.T).item()
    return sim ** 3

def get_content_score(msg):
    with torch.no_grad():
        inputs = contnet_tokenizer(msg, return_tensors="pt", padding=True, truncation=True).to(speech_sim_model.device)
        output = content_model(**inputs)
    return output.items()

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
    query_vector = calc_tone_embedding(query)#embedding_model.encode(query)
    query_vector = np.array(query_vector).reshape(1, -1).astype('float32')
    
    # FAISS를 사용하여 유사한 벡터 검색
    print(query_vector.shape, vectors.shape)
    distances, indices = index.search(query_vector, min(top_k, len(vectors)))   # [[0.84129953]] [[0]]
    
    print(distances)
    for idx in indices[0]:
        print(texts[idx])
    
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