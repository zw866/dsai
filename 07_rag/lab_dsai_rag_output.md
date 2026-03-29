# Lab RAG Output

## Query
How can I build a dashboard that answers questions with project documents?

## Retrieved Records
```json
{
  "query": "How can I build a dashboard that answers questions with project documents?",
  "document": "dsai_project_notes.csv",
  "matches": [
    {
      "id": 2,
      "topic": "Productivity Dashboard",
      "goal": "Build an interactive dashboard that summarizes project metrics for non-technical users",
      "tools": "Shiny, Python, HTML",
      "deliverable": "Interactive dashboard and summary report",
      "keywords": "dashboard, shiny, report, visualization, metrics"
    },
    {
      "id": 3,
      "topic": "AI Query Assistant",
      "goal": "Answer user questions with evidence from project documents and generated reports",
      "tools": "LLM, prompt engineering, markdown",
      "deliverable": "Question answering workflow and written report",
      "keywords": "llm, rag, query, documents, evidence"
    },
    {
      "id": 4,
      "topic": "Deployment Workflow",
      "goal": "Publish an app so it can run outside the local machine with minimal manual setup",
      "tools": "GitHub Actions, Posit Connect, Docker",
      "deliverable": "Deployable app with setup instructions",
      "keywords": "deploy, hosting, workflow, automation, production"
    },
    {
      "id": 6,
      "topic": "Custom RAG Prototype",
      "goal": "Search project records before sending context to the model so answers stay grounded",
      "tools": "Python, pandas, Ollama",
      "deliverable": "RAG script and output screenshot",
      "keywords": "rag, retrieval, context, grounded, search"
    },
    {
      "id": 8,
      "topic": "Final Project Report",
      "goal": "Combine code results and narrative explanation into a polished deliverable for submission",
      "tools": "Markdown, HTML, DOCX",
      "deliverable": "Final report package and presentation notes",
      "keywords": "report, summary, deliverable, writeup, presentation"
    }
  ],
  "num_matches": 5
}
```

## Model Response
### Summary: Building a Productivity Dashboard for Non-Technical Users

**Dashboard Components:**
1. Interactive dashboard with project metrics visualization using Shiny and Python
2. Written summary report highlighting key findings from project documents
3. User interaction with generated reports to understand project progress
4. Use of AI query assistant, LLM, prompt engineering, and markdown for answering user questions

**Relevant Project Records:**
1. "dsai_project_notes.csv" (CSV file containing project notes)
2. "Final Project Report" (document with deliverable guidelines)
3. "Productivity Dashboard" (topic of the query)
4. "AI Query Assistant" (goal and tools for delivering AI-powered answers)
5. "Deployment Workflow" (deliverable and keywords related to deployment process)
