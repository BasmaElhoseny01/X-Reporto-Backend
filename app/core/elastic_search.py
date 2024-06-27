from elasticsearch import Elasticsearch
from app.core.config import configs


class ElasticsSearch:
    def __init__(self):
        self.client = Elasticsearch([configs.ELASTICSEARCH_URL])

    def create_index(self, index_name, body):
        if not self.client.indices.exists(index=index_name):
            self.client.indices.create(index=index_name, body=body)

    def index_document(self, index_name, doc_id, document):
        self.client.index(index=index_name, id=doc_id, body=document)

    def search(self, index_name, body):
        return self.client.search(index=index_name, body=body)