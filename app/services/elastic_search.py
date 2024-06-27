from app.repository.elastic_search import ElasticSearchRepository
from app.models.elastic_search import Document

class SearchService:
    def __init__(self, es_repo: ElasticSearchRepository):
        self.es_repo = es_repo

    def index_document(self, document: Document):
        self.es_repo.index_document(document)

    def search_documents(self, query: str):
        return self.es_repo.search_documents(query)

