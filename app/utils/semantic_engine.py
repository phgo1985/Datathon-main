from langchain.schema import Document
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def gerar_embedding(texto):
    return embedding_model.encode(texto)

def preparar_documentos(lista_textos):
    return [Document(page_content=txt) for txt in lista_textos]

def criar_vector_store(textos):
    docs = preparar_documentos(textos)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_documents(docs, embedding=embeddings)

def buscar_similaridade(query, vector_store, k=5):
    return vector_store.similarity_search(query, k=k)