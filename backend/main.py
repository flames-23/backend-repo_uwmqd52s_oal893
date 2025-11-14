from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os

from database import db, create_document, get_documents
from schemas import Contact, Lead, VisitorEvent, Project

app = FastAPI(title="Portfolio API", version="1.0.0")

# CORS for frontend
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*" if FRONTEND_URL == "*" else FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Backend is running", "backend": "FastAPI"}


@app.get("/test")
async def test_db():
    # probe DB connection and list collections
    try:
        names = await db.list_collection_names()
        return {
            "backend": "FastAPI",
            "database": "MongoDB",
            "database_url": os.getenv("DATABASE_URL", "mongodb://localhost:27017"),
            "database_name": os.getenv("DATABASE_NAME", "appdb"),
            "connection_status": "connected",
            "collections": names,
        }
    except Exception as e:
        return {
            "backend": "FastAPI",
            "database": "MongoDB",
            "connection_status": f"error: {e}",
        }


@app.post("/contact")
async def create_contact(contact: Contact):
    saved = await create_document("contact", contact.model_dump())
    return {"status": "ok", "data": saved}


@app.post("/lead")
async def create_lead(lead: Lead):
    saved = await create_document("lead", lead.model_dump())
    return {"status": "ok", "data": saved}


@app.post("/event")
async def track_event(evt: VisitorEvent):
    saved = await create_document("visitorevent", evt.model_dump())
    return {"status": "ok", "data": saved}


# Seed endpoint to pre-populate projects based on the resume
@app.post("/seed-projects")
async def seed_projects():
    projects: List[Project] = [
        Project(
            title="Production-Grade Multi-Tier AWS Architecture",
            summary=(
                "Highly available multi-tier infra with global CDN and intelligent DNS. Auto-scaling, multi-AZ RDS, "
                "Terraform modules for repeatable deployments. 99.99% uptime; 10x traffic spikes handled; 85% faster provisioning."
            ),
            tech=["AWS", "EC2", "RDS", "ALB", "ASG", "Route53", "CloudFront", "Terraform"],
            links={"readme": "#"},
        ),
        Project(
            title="Enterprise-Grade CI/CD DevOps Pipeline",
            summary=(
                "Jenkins + Docker + K8s with SonarQube and Trivy gates. Rolling updates, zero downtime releases, Prometheus "
                "metrics and custom Grafana dashboards for pipeline and app monitoring."
            ),
            tech=["Jenkins", "Docker", "Kubernetes", "SonarQube", "Trivy", "Prometheus", "Grafana"],
            links={"readme": "#"},
        ),
        Project(
            title="ChatOps Infrastructure Automation Platform",
            summary=(
                "Slack bot to provision AWS via natural language using Lambda + API Gateway + boto3; EC2 self-serve in <30s."
            ),
            tech=["Slack API", "AWS Lambda", "API Gateway", "Python", "boto3", "DynamoDB"],
            links={"readme": "#"},
        ),
        Project(
            title="Ethereum Node on Amazon Managed Blockchain",
            summary=(
                "AWS CDK defined infra for Ethereum node with PrivateLink access, IAM scoped permissions, and CloudWatch monitoring."
            ),
            tech=["AWS CDK", "Managed Blockchain", "Python", "IAM", "S3"],
            links={"readme": "#"},
        ),
    ]

    created = []
    for p in projects:
        created.append(await create_document("project", p.model_dump()))

    return {"status": "ok", "count": len(created), "data": created}


@app.get("/projects")
async def list_projects(limit: int = 10):
    docs = await get_documents("project", limit=limit)
    return {"status": "ok", "data": docs}
