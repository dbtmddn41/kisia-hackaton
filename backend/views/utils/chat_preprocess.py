import pandas as pd
import re

# 카톡 데이터 기본 전처리 클래스
class ChatProcessor:
    def __init__(self, path, client_name, person_name, exclude_list=None):
        self.path = path
        self.client_name = client_name
        self.person_name = person_name
        self.file_name = f"{client_name}_{person_name}_chat.txt"
        self.chat_df = None
        self.client_chat_list = []
        self.person_chat_list = []
        self.exclude_list = exclude_list if exclude_list is not None else []

    def load_data(self):
        data = pd.read_csv(self.path + self.file_name, sep='\t', engine='python', encoding='utf-8')
        title = list(data)
        chat_list = []
        
        for i in data[title[0]]:
            content = i.split(',', 1)
            try:
                content2 = content[1].split(':', 1)
                chat_list.append(content[0] + ',' + content2[0] + ',' + content2[1])
            except:
                continue

        col_name = []
        col_content = []

        for content in chat_list:
            split_list = content.split(',', 2)
            # 카카오톡 이모티콘을 보내면 대화내역 .txt 파일에 
            # "이모티콘" 글자만 뜨기 때문에 추가하지 않음
            # 안내메시지 리스트(제외 리스트)에 있는 문자열이라면 추가하지 않음
            content_data = self._remove_emails(split_list[2].strip())
            if not self._remove_excluded_chat(content_data) and not self._remove_urls(content_data) and content_data != "이모티콘":
                col_name.append(split_list[1])
                col_content.append(content_data)
            else :
                continue

        self.chat_df = pd.DataFrame(data=col_name, columns=['name'])
        self.chat_df['content'] = col_content

    def _remove_emails(self, text):
        email_pattern = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        )
        # 이메일 주소를 찾아서 빈 문자열로 교체
        cleaned_text = email_pattern.sub('', text)
        return cleaned_text

    def _remove_urls(self, text):
        if "https://www." in text :
            return True
        return False
    
    def _remove_excluded_chat(self, text):
        # 텍스트에 제외 리스트의 문자열이 포함되어 있는지 확인
        for phrase in self.exclude_list:
            if phrase in text:
                return True
        return False

    def process_client_chat(self):
        if self.chat_df is not None:
            client_df = self.chat_df[self.chat_df['name'] == f' {self.client_name} ']
            self.client_chat_list = list(client_df['content'])

    def process_person_chat(self):
        if self.chat_df is not None:
            person_df = self.chat_df[self.chat_df['name'] == f' {self.person_name} ']
            self.person_chat_list = list(person_df['content'])

    def get_client_chats(self):
        return self.client_chat_list

    def get_person_chats(self):
        return self.person_chat_list 
    
    def save_person_chat_data_to_csv(self):
        df = pd.DataFrame(self.get_person_chats(), columns=[self.person_name])
        df.to_csv(self.path + self.person_name + "_data.csv" , index=False, encoding='utf-8')

    def save_client_chat_data_to_csv(self):
        df = pd.DataFrame(self.get_client_chats(), columns=[self.client_name])
        df.to_csv(self.path + self.client_name + "_data.csv", index=False, encoding='utf-8')
