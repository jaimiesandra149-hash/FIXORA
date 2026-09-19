from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="FIXORA")
sessions = {}

class TroubleshootingRequest(BaseModel):
    problem: str


# Prototype action catalog
ACTION_CATALOG = {
    "performance": [
        {
            "step": 1,
            "title": "Restart the device",
            "type": "auto",
            "status": "ready",
            "deeplink": None
        },
        {
            "step": 2,
            "title": "Check available storage",
            "type": "manual",
            "status": "ready",
            "deeplink": None
        },
        {
            "step": 3,
            "title": "Check for additional software updates",
            "type": "manual",
            "status": "ready",
            "deeplink": None
        }
    ],

    "battery": [
        {
            "step": 1,
            "title": "Restart the device",
            "type": "auto",
            "status": "ready",
            "deeplink": None
        },
        {
            "step": 2,
            "title": "Check battery usage",
            "type": "manual",
            "status": "ready",
            "deeplink": None
        },
        {
            "step": 3,
            "title": "Check battery and device care",
            "type": "manual",
            "status": "ready",
            "deeplink": None
        }
    ],

    "display": [
        {
            "step": 1,
            "title": "Restart the device",
            "type": "auto",
            "status": "ready",
            "deeplink": None
        },
        {
            "step": 2,
            "title": "Check display settings",
            "type": "manual",
            "status": "ready",
            "deeplink": None
        }
    ],

    "general": [
        {
            "step": 1,
            "title": "Restart the device",
            "type": "auto",
            "status": "ready",
            "deeplink": None
        }
    ]
}


# Query Enrichment
def enrich_query(problem: str):
    text = problem.lower()

    category = "general"
    symptoms = []
    triggers = []

    if any(word in text for word in ["slow", "lag", "freeze", "stuck"]):
        category = "performance"
        symptoms.append("device is slow")

    if any(word in text for word in [
        "battery",
        "drain",
        "dies fast",
        "charge"
    ]):
        category = "battery"
        symptoms.append("battery drains quickly")

    if any(word in text for word in [
        "flicker",
        "flickering",
        "screen",
        "display"
    ]):
        category = "display"
        symptoms.append("display issue")

    if any(word in text for word in [
        "update",
        "updated",
        "software update"
    ]):
        triggers.append("software update")

    return {
        "device": "Galaxy device",
        "category": category,
        "symptoms": symptoms,
        "triggers": triggers
    }


@app.get("/")
def home():
    return {
        "message": "FIXORA Troubleshooting Engine is running!"
    }


@app.post("/troubleshoot")
def troubleshoot(request: TroubleshootingRequest):

    issue = enrich_query(request.problem)

    actions = ACTION_CATALOG.get(
        issue["category"],
        ACTION_CATALOG["general"]
    )

    return {
        "problem": request.problem,
        "issue": issue,
        "actions": actions,
        "verification": {
            "question": "Is your device working normally now?",
            "options": [
                "Yes, the issue is fixed",
                "No, the issue continues"
            ]
        },
        "metadata": {
            "cache_hit": False
        }
    }
@app.post("/troubleshoot/start")
def start_troubleshooting(request: TroubleshootingRequest):

    issue = enrich_query(request.problem)

    actions = ACTION_CATALOG.get(
        issue["category"],
        ACTION_CATALOG["general"]
    )

    session_id = str(len(sessions) + 1)

    sessions[session_id] = {
        "problem": request.problem,
        "issue": issue,
        "actions": actions,
        "current_step": 0
    }

    current_action = actions[0]

    return {
        "session_id": session_id,
        "problem": request.problem,
        "progress": {
            "current": 1,
            "total": len(actions)
        },
        "current_action": current_action,
        "message": "Follow this step and then confirm when completed."
    }
@app.post("/troubleshoot/{session_id}/complete")
def complete_step(session_id: str):

    if session_id not in sessions:
        return {
            "error": "Troubleshooting session not found"
        }

    session = sessions[session_id]

    session["current_step"] += 1

    if session["current_step"] >= len(session["actions"]):
        return {
            "session_id": session_id,
            "status": "completed",
            "message": "All troubleshooting steps have been completed.",
            "verification": {
                "question": "Is your device working normally now?",
                "options": [
                    "Yes, the issue is fixed",
                    "No, the issue continues"
                ]
            }
        }

    next_action = session["actions"][session["current_step"]]

    return {
        "session_id": session_id,
        "status": "in_progress",
        "progress": {
            "current": session["current_step"] + 1,
            "total": len(session["actions"])
        },
        "current_action": next_action,
        "message": "Complete this step before continuing."
           }