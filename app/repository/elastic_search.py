from app.core.elastic_search import ElasticsSearch
from app.models.elastic_search import Document

class ElasticSearchRepository:
    def __init__(self, es_client: ElasticsSearch):
        self.es_client = es_client

    def index_document(self, document: Document):
        doc_dict = document.dict()
        self.es_client.index_document(index_name='documents', doc_id=document.id, document=doc_dict)

    def search_documents(self, query: str):
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "content"]
                }
            }
        }
        return self.es_client.search(index_name='documents', body=body)
