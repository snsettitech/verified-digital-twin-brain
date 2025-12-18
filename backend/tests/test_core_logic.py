import pytest
from unittest.mock import MagicMock, patch
from modules.retrieval import retrieve_context
from modules.answering import generate_answer

def test_retrieve_context_structure():
    # Mock Pinecone index
    mock_index = MagicMock()
    mock_index.query.return_value = {
        "matches": [
            {
                "score": 0.9,
                "metadata": {"text": "This is a test chunk", "source_id": "src-123"}
            }
        ]
    }
    
    with patch("modules.retrieval.get_pinecone_index", return_value=mock_index), \
         patch("modules.retrieval.get_embedding", return_value=[0.1]*3072):
        
        results = retrieve_context("test query", "twin-456")
        
        assert len(results) == 1
        assert results[0]["text"] == "This is a test chunk"
        assert results[0]["score"] == 0.9
        assert results[0]["source_id"] == "src-123"

def test_generate_answer_citations():
    mock_contexts = [
        {"text": "Sample knowledge", "score": 0.8, "source_id": "src-1"}
    ]
    
    mock_openai_response = MagicMock()
    mock_openai_response.choices[0].message.content = "The answer is here [Source 1]"
    
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_openai_response
    
    with patch("modules.answering.get_openai_client", return_value=mock_client):
        result = generate_answer("test query", mock_contexts)
        
        assert "answer" in result
        assert "[Source 1]" in result["answer"]
        assert result["confidence_score"] == 0.8
        assert result["citations"] == ["src-1"]
