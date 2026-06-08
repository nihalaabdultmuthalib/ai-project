from fastapi.testclient import TestClient

from app.main import app, get_qa_service


class FakeQAService:
    async def ingest(self, source: str, content: str) -> list[int]:
        assert source
        assert content
        return [1]

    async def ask(self, question: str) -> tuple[str, list[dict]]:
        return (
            f"Mock answer for: {question}",
            [
                {
                    "id": 1,
                    "source": "test.txt",
                    "content": "FastAPI service with PostgreSQL pgvector retrieval.",
                    "score": 0.91,
                }
            ],
        )

    async def list_documents(self, limit: int = 20) -> list[dict]:
        return [
            {
                "id": 1,
                "source": "test.txt",
                "content": "FastAPI service with PostgreSQL pgvector retrieval.",
                "created_at": None,
            }
        ][:limit]


def override_qa_service() -> FakeQAService:
    return FakeQAService()


def test_home():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["docs_url"] == "/docs"


def test_ingest_document():
    app.dependency_overrides[get_qa_service] = override_qa_service
    client = TestClient(app)

    response = client.post(
        "/documents",
        json={
            "source": "test.txt",
            "content": "This is enough content to pass validation for the ingestion endpoint.",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json() == {"ids": [1], "source": "test.txt"}


def test_ask_question():
    app.dependency_overrides[get_qa_service] = override_qa_service
    client = TestClient(app)

    response = client.post("/ask", json={"question": "What does the project use?"})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Mock answer for: What does the project use?"
    assert body["sources"][0]["source"] == "test.txt"


def test_list_documents():
    app.dependency_overrides[get_qa_service] = override_qa_service
    client = TestClient(app)

    response = client.get("/documents")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["id"] == 1
