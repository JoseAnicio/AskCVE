import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq
from config import GROQ_API_KEY

@st.cache_resource
def load_model():
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="cves")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    llm = ChatGroq(api_key=GROQ_API_KEY, model_name="llama-3.1-8b-instant")
    return collection, model, llm

def ask(asking, collection, model, llm):
    embedding = model.encode(asking).tolist()
    results = collection.query(query_embeddings=[embedding], n_results=5)
    context = "\n\n".join(results["documents"][0])
    prompt = f"""You are a cybersecurity expert. Based on the following vulnerabilities, answer the question:

{context}
Question: {asking}
"""
    return llm.invoke(prompt).content

st.title("Cybersecurity CVE Q&A")
st.caption("Ask questions about cybersecurity vulnerabilities related to Apache, Nginx, OpenSSL, Linux, WordPress, MySQL, SSH, and PHP.")

collection, model, llm = load_model() 

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if asking := st.chat_input("Ask a question about cybersecurity vulnerabilities..."):
    st.chat_message("user").write(asking)
    st.session_state.messages.append({"role": "user", "content": asking})

    with st.chat_message("assistant"):
        with st.spinner("Searching for relevant CVEs..."):
            answer = ask(asking, collection, model, llm)
        st.write(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
