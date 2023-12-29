import os
import sys
import json

from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import Chroma
from website import constants

# Other constants
os.environ["OPENAI_API_KEY"] = constants.APIKEY
PERSIST = False

query = None
if len(sys.argv) > 1:
    query = sys.argv[1]

if PERSIST and os.path.exists("persist"):
    print("Reusing index...\n")
    vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
    index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:   
    loader1 = TextLoader("website/data/ecommerce.json")
    loader2 = TextLoader("website/data/data.txt")
    loader3 = TextLoader("website/data/owner.txt")



    if PERSIST:
        index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory": "persist"}).from_loaders([loader1, loader2,loader3])
    else:
        index = VectorstoreIndexCreator().from_loaders([loader1, loader2 , loader3])

chain = ConversationalRetrievalChain.from_llm(
    llm=ChatOpenAI(model="gpt-3.5-turbo"),
    retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
)

chat_history = []

def get_chatbot_response(query, chat_history):
    result = chain({"question": query, "chat_history": chat_history})
    chat_history.append((query, result['answer']))
    return result['answer']


#real code now