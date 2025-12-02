import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

API_KEY = os.getenv("API_KEY")
#BASE_URL = "https://aleron-llm.neuraldeep.tech/"

# LLM (для диалогов, не обязателен для эмбеддингов)
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=API_KEY,
    #base_url=BASE_URL,
    temperature=0
)

# Модель эмбеддингов 
embeddings_model = OpenAIEmbeddings(
    model="text-embedding-3-small",   
    api_key=API_KEY
    #base_url=BASE_URL,
)

# Разбивка текста на чанки
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,     # размер чанка (символы)
    chunk_overlap=200,  # перекрытие
)

def chunk_and_embed_to_db(text: str, conn):
    docs = text_splitter.create_documents([text])
    chunks = [d.page_content for d in docs]

    vectors = embeddings_model.embed_documents(chunks)

    cursor = conn.cursor()
    for chunk, vec in zip(chunks, vectors):
        # pgvector принимает вот такой строчный формат: [1,2,3,...]
        vec_str = "[" + ",".join(str(x) for x in vec) + "]"
        cursor.execute(
            """
            INSERT INTO embeddings (text, embedding)
            VALUES (%s, %s::vector)
            """,
            (chunk, vec_str),
        )

    return len(chunks)

def get_top_k_chunks(question: str, conn, k: int = 3) -> list[str]:
    """Векторизуем вопрос и достаём top-k ближайших чанков из таблицы embeddings."""
    # один вектор для запроса
    q_vec = embeddings_model.embed_query(question)
    q_vec_str = "[" + ",".join(str(x) for x in q_vec) + "]"

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT text
        FROM embeddings
        ORDER BY embedding <-> %s::vector
        LIMIT %s
        """,
        (q_vec_str, k),
    )
    rows = cursor.fetchall()
    return [r[0] for r in rows]