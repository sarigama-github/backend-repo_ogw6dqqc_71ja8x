import os
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Mental Health Awareness API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuizAnswer(BaseModel):
    answers: List[int]


@app.get("/")
def read_root():
    return {"message": "Mental Health Awareness API is running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/api/resources")
def get_resources() -> Dict[str, Any]:
    resources = [
        {
            "title": "Understanding Anxiety",
            "description": "Learn what anxiety is, common symptoms, and ways to cope.",
            "url": "https://www.nimh.nih.gov/health/topics/anxiety-disorders",
            "category": "Education",
        },
        {
            "title": "Depression: Signs and Support",
            "description": "Recognize signs of depression and explore evidence-based treatments.",
            "url": "https://www.who.int/news-room/fact-sheets/detail/depression",
            "category": "Education",
        },
        {
            "title": "Mindfulness Exercises",
            "description": "Short, practical mindfulness techniques to ground yourself.",
            "url": "https://www.mindful.org/meditation/mindfulness-getting-started/",
            "category": "Self-Care",
        },
        {
            "title": "Finding a Therapist",
            "description": "Tips and directories to start therapy in your region.",
            "url": "https://www.psychologytoday.com/us/therapists",
            "category": "Support",
        },
        {
            "title": "Coping with Stress",
            "description": "WHO guide to managing stress with practical strategies.",
            "url": "https://www.who.int/publications/i/item/9789240003927",
            "category": "Self-Care",
        },
    ]
    tips = [
        "Breathe: Try 4-7-8 breathing for one minute.",
        "Move: A 10-minute walk can shift your mood.",
        "Connect: Text a friend and share how you’re feeling.",
        "Nourish: Drink water and have a balanced snack.",
        "Rest: Aim for a consistent sleep routine.",
    ]
    return {"resources": resources, "tips": tips}


@app.get("/api/helplines")
def get_helplines() -> Dict[str, Any]:
    helplines = [
        {
            "region": "United States",
            "name": "988 Suicide & Crisis Lifeline",
            "contact": "Call or text 988 | chat 988lifeline.org",
            "url": "https://988lifeline.org/",
        },
        {
            "region": "United Kingdom",
            "name": "Samaritans",
            "contact": "116 123 | jo@samaritans.org",
            "url": "https://www.samaritans.org/",
        },
        {
            "region": "Canada",
            "name": "Talk Suicide Canada",
            "contact": "1-833-456-4566 | text 45645",
            "url": "https://www.talksuicide.ca/",
        },
        {
            "region": "Australia",
            "name": "Lifeline Australia",
            "contact": "13 11 14 | lifeline.org.au",
            "url": "https://www.lifeline.org.au/",
        },
        {
            "region": "International",
            "name": "Find a helpline",
            "contact": "findahelpline.com",
            "url": "https://findahelpline.com/",
        },
    ]
    return {"helplines": helplines}


@app.post("/api/quiz")
def score_quiz(payload: QuizAnswer) -> Dict[str, Any]:
    if not payload.answers or any(a not in [0, 1, 2, 3] for a in payload.answers):
        raise HTTPException(status_code=400, detail="Answers must be a list of integers 0-3")

    score = sum(payload.answers)
    level = ""
    suggestion = ""

    if score <= 6:
        level = "Low"
        suggestion = "You seem to be doing okay. Keep up your routines and check in with yourself." \
                     " Explore the tips section for daily maintenance."
    elif score <= 12:
        level = "Moderate"
        suggestion = "You may be experiencing some stress. Consider mindfulness, movement, and talking to someone you trust."
    elif score <= 18:
        level = "Elevated"
        suggestion = "It might help to speak with a mental health professional. Check the helplines and consider scheduling a consult."
    else:
        level = "High"
        suggestion = "Please consider reaching out to a professional or a trusted person today. If you feel unsafe, contact your local crisis line immediately."

    return {"score": score, "level": level, "suggestion": suggestion}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
