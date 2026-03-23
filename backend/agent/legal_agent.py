"""
agent/legal_agent.py
────────────────────
LangChain agent that:
1. Stores gold-standard clause templates in ChromaDB (RAG)
2. Compares uploaded clauses against standards (semantic similarity)
3. Answers follow-up questions with conversational memory
4. Generates plain-English redline suggestions
"""

import os
from typing import List, Dict
from urllib import response
from groq import Groq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.tools import Tool
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage


# ---------------------------------------------------------------------------
# Gold-standard template clauses (seeded into ChromaDB on first run)
# ---------------------------------------------------------------------------
TEMPLATE_CLAUSES = [
    {
        "id": "nda_standard",
        "category": "Confidentiality / NDA",
        "text": (
            "Each party agrees to hold the other's Confidential Information in strict confidence "
            "and not to disclose it to any third party without prior written consent. "
            "This obligation shall survive termination for a period of two (2) years."
        ),
    },
    {
        "id": "liability_cap_standard",
        "category": "Liability Cap",
        "text": (
            "In no event shall either party's aggregate liability exceed the total fees paid "
            "in the six (6) months preceding the claim. Neither party shall be liable for "
            "indirect, incidental, or consequential damages."
        ),
    },
    {
        "id": "termination_standard",
        "category": "Termination",
        "text": (
            "Either party may terminate this Agreement upon thirty (30) days written notice. "
            "Termination for cause may be effected immediately upon written notice if the other "
            "party materially breaches this Agreement and fails to cure within fifteen (15) days."
        ),
    },
    {
        "id": "noncompete_standard",
        "category": "Non-Compete",
        "text": (
            "During the term and for a period of twelve (12) months thereafter, Employee shall not "
            "engage in any business that directly competes with the Company in the geographic "
            "regions where the Company currently operates."
        ),
    },
    {
        "id": "ip_standard",
        "category": "Intellectual Property",
        "text": (
            "All work product, inventions, and deliverables created by Contractor in the course of "
            "performing Services shall be considered works made for hire and shall be the sole "
            "property of the Client."
        ),
    },
    {
        "id": "governing_law_standard",
        "category": "Governing Law",
        "text": (
            "This Agreement shall be governed by and construed in accordance with the laws of the "
            "State of Delaware, without regard to conflicts of law principles."
        ),
    },
]


class LegalAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)
        self.vectorstore = self._build_vectorstore()
        self._last_context = ""

    # -----------------------------------------------------------------------
    # Vector store setup
    # -----------------------------------------------------------------------
    def _build_vectorstore(self) -> Chroma:
        """Seed ChromaDB with gold-standard templates."""
        texts = [t["text"] for t in TEMPLATE_CLAUSES]
        metadatas = [{"id": t["id"], "category": t["category"]} for t in TEMPLATE_CLAUSES]

        vs = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            collection_name="legal_templates",
            persist_directory="./chroma_db",
        )
        return vs

    def _find_similar_template(self, clause_text: str, k: int = 1) -> List[Dict]:
        """Return the top-k most similar template clauses."""
        results = self.vectorstore.similarity_search_with_score(clause_text, k=k)
        return [
            {
                "text": doc.page_content,
                "category": doc.metadata.get("category"),
                "similarity": round(1 - score, 3),  # cosine distance → similarity
            }
            for doc, score in results
        ]

    # -----------------------------------------------------------------------
    # LangChain tools
    # -----------------------------------------------------------------------
    def _tool_compare_clause(self, clause: str) -> str:
        """Compare clause against gold-standard templates."""
        matches = self._find_similar_template(clause, k=1)
        if not matches:
            return "No comparable standard clause found."
        m = matches[0]
        return (
            f"Most similar standard: [{m['category']}] (similarity: {m['similarity']})\n"
            f"Standard text: {m['text']}\n"
            f"Deviation detected: {'Yes' if m['similarity'] < 0.80 else 'No significant deviation'}"
        )

    def _tool_suggest_redline(self, clause: str) -> str:
        prompt = (
            "You are a legal expert reviewing a contract clause. "
            "Identify any risky or unusual terms and suggest a safer alternative wording.\n\n"
            f"Clause: {clause}"
        )

        response = self.client.chat.completions.create(
            model="groq/compound",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    def _tool_summarize_risk(self, clause: str) -> str:
        """Summarize risk of a clause in plain English."""
        prompt = (
            "Summarize the key legal risks of this clause in 2–3 plain-English sentences "
            "suitable for a startup founder with no legal background.\n\n"
            f"Clause: {clause}"
        )
        response = self.client.chat.completions.create(
        model="groq/compound",
        messages=[{"role": "user", "content": prompt}]
)

        return response.choices[0].message.content

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------
    def summarize(self, classified_segments):
        context = "\n\n".join(
            f"{s['category']} ({s['risk']}): {s['text'][:200]}"
            for s in classified_segments[:10]
        )

        prompt = f"""
        Summarize this contract in clean plain English.

        IMPORTANT:
        - Do NOT use markdown
        - Do NOT use tables
        - Do NOT use symbols like |, ---, **
        - Use simple bullet points
        - Keep it clean and readable

        {context}
    """

        response = self.client.chat.completions.create(
            model="groq/compound",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    def chat(self, question: str, context: str = ""):
        prompt = f"""
        Context:
        {context}

        Question:
        {question}
        """

        response = self.client.chat.completions.create(
            model="groq/compound",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content
