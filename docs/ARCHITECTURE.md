# Infosys Compliance Checker V2 Architecture

## Purpose

Second iteration of the compliance checker with document analysis workflow improvements.

## Stack

Python, FastAPI, Streamlit, ChromaDB, PyPDF2

## System Context

```mermaid
flowchart LR
    User["Commercial contract PDF"] --> App["FastAPI compliance engine and ChromaDB manager"]
    App --> Data["Contract text, regulatory knowledge, vector retrieval"]
    App --> Output["Risk and compliance summary"]
    Data --> Output
```
## Runtime Workflow

```mermaid
flowchart TD
    S1["Upload document"] --> S2["Parse text"]
    S2["Parse text"] --> S3["Retrieve related regulations"]
    S3["Retrieve related regulations"] --> S4["Score compliance risks"]
    S4["Score compliance risks"] --> S5["Display reviewer-ready summary"]
```
## Production Readiness Notes

- Keep secrets in environment variables and commit only .env.example templates.
- Keep generated files, dependency folders, caches, and local databases out of version control.
- Run the GitHub Actions workflow before presenting or deploying changes.
- Update this document when the source layout, dependencies, or deployment model changes.

## Review Checklist

- Architecture diagram matches current source files.
- Workflow diagram matches the main user or data path.
- README links to this architecture document.
- CI workflow validates the project on every push and pull request.

