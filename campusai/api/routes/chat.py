"""
Chat and conversational helpdesk endpoints.
"""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from campusai.api.dependencies import get_current_user, get_db
from campusai.api.schemas import ChatRequest, ChatResponse, CitationOut, FeedbackRequest
from campusai.database.models import (
    ChatMessage, ChatSession, Feedback, ResponseCitation, User
)
from campusai.nlp.coreference import ConversationContext
from campusai.rag.generator import ConversationalRAGEngine

router = APIRouter(prefix="/chat", tags=["Student Helpdesk Chat"])

# Global RAG Engine singleton
rag_engine = ConversationalRAGEngine()


@router.post("", response_model=ChatResponse)
def send_chat_message(
    req: ChatRequest,
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a question to the CampusAI academic helpdesk."""
    session_id = req.session_id or str(uuid.uuid4())

    # Get or create chat session
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        session = ChatSession(
            id=session_id,
            user_id=user.id if user else None,
            department_code=req.department_code,
            curriculum_version=req.curriculum_version,
            title=req.query[:40] + ("..." if len(req.query) > 40 else "")
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    # Load recent conversation history for memory
    past_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(6)
        .all()
    )
    turn_history = [{"role": m.role, "content": m.content} for m in past_messages]

    ctx = ConversationContext(
        session_id=session_id,
        last_department=session.department_code or req.department_code,
        turn_history=turn_history
    )

    # Process query through RAG engine
    result = rag_engine.process_query(
        query=req.query,
        context=ctx,
        department_hint=req.department_code
    )

    # Persist user message
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=req.query,
        intent=result.get("intent"),
        entities=result.get("entities")
    )
    db.add(user_msg)
    db.commit()

    # Persist assistant message
    asst_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=result["answer"],
        intent=result.get("intent"),
        entities=result.get("entities")
    )
    db.add(asst_msg)
    db.commit()
    db.refresh(asst_msg)

    # Persist citations
    citation_outs: List[CitationOut] = []
    for cit in result.get("citations", []):
        rc = ResponseCitation(
            message_id=asst_msg.id,
            source_doc_id=cit["doc_id"],
            source_title=cit["title"],
            department_code=cit["department"],
            source_page=cit["page"],
            source_excerpt=cit["excerpt"],
            course_code=cit.get("course_code")
        )
        db.add(rc)
        citation_outs.append(CitationOut(**cit))
    db.commit()

    return ChatResponse(
        answer=result["answer"],
        intent=result.get("intent", "course_search"),
        domain=result.get("domain", "curriculum"),
        language=result.get("language", "en"),
        session_id=session_id,
        entities=result.get("entities", {}),
        citations=citation_outs,
        source_type=result.get("source_type", "hybrid_rag"),
        is_grounded=result.get("is_grounded", True)
    )


@router.get("/sessions")
def list_sessions(user: Optional[User] = Depends(get_current_user), db: Session = Depends(get_db)):
    """List recent chat sessions."""
    query = db.query(ChatSession)
    if user:
        query = query.filter(ChatSession.user_id == user.id)
    sessions = query.order_by(ChatSession.updated_at.desc()).limit(20).all()
    return [
        {
            "id": s.id,
            "title": s.title,
            "department_code": s.department_code,
            "curriculum_version": s.curriculum_version,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}")
def get_session_history(session_id: str, db: Session = Depends(get_db)):
    """Retrieve full message history and citations for a chat session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    formatted = []
    for m in messages:
        cits = [
            {
                "doc_id": c.source_doc_id,
                "title": c.source_title,
                "department": c.department_code,
                "page": c.source_page,
                "excerpt": c.source_excerpt,
                "course_code": c.course_code
            }
            for c in m.citations
        ]
        formatted.append({
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "intent": m.intent,
            "citations": cits,
            "created_at": m.created_at.isoformat() if m.created_at else None
        })

    return {
        "session_id": session.id,
        "title": session.title,
        "department_code": session.department_code,
        "messages": formatted
    }


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a chat session and its messages per privacy requirements."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(session)
    db.commit()
    return {"message": f"Session {session_id} successfully deleted."}


@router.post("/feedback")
def submit_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    """Submit student feedback on an answer."""
    fb = Feedback(
        session_id=req.session_id,
        message_id=req.message_id,
        rating=req.rating,
        category=req.category,
        comments=req.comments
    )
    db.add(fb)
    db.commit()
    return {"status": "success", "message": "Feedback received. Thank you!"}
