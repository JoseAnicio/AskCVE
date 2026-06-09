import requests
import chromadb
from sentence_transformers import SentenceTransformer
from config import GROQ_API_KEY

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="cves")
model = SentenceTransformer('all-MiniLM-L6-v2')

KEYWORDS = ["apache", "nginx", "openssl", "linux kernel", "wordpress", "mysql", "ssh", "php"]

def search_cves(keyword, total=100):
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={keyword}&resultsPerPage={total}"
    response = requests.get(url)
    dados = response.json()

    cves = []
    for item in dados["vulnerabilities"]:
        cve_id = item["cve"]["id"]
        description = item["cve"]["descriptions"][0]["value"]
        cves.append({"id": cve_id, "description": description})

    print (cves)
    return cves

def index_cves(keyword):
    for keyword in KEYWORDS:
        print(f"Indexing CVEs for keyword: {keyword}")
        cves = search_cves(keyword)
        print(f"Found {len(cves)} CVEs for keyword. Indexing into ChromaDB...")

        for cve in cves:
            embedding = model.encode(cve["description"]).tolist()
            collection.upsert(
                ids=[cve["id"]],
                documents=[cve["description"]],
                embeddings=[embedding],
                metadatas=[{"cve_id": cve["id"], "keyword": keyword}]
            )

if __name__ == "__main__":
    index_cves("apache")

