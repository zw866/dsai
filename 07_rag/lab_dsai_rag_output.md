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
**Project Planning Report Summary**

This project aims to build a dashboard that answers questions with project documents using the following tools:

* Shiny for interactive dashboards
* Python for generating reports and visualizations
* HTML for structuring content
* Markdown for writing documentation
* LLM (Language Model) for question answering
* Prompt engineering for improving response quality
* Docker for deployment and continuous integration

Key components that need to be completed:

1. **Productivity Dashboard**: Build an interactive dashboard with metrics visualization, summary report, and actionable insights for non-technical users. Tools: Shiny, Python, HTML. Deliverable: Interactive dashboard, summary report. Keywords: dashboard, shiny, report, visualization, metrics.
2. **AI Query Assistant**: Answer user questions using evidence from project documents and generated reports with evidence from LLM. Tools: LLMs (Language Model), prompt engineering, markdown. Deliverable: Question answering workflow and written report. Keywords: llm, rag, query, documents, evidence.
3. **Deployment Workflow**: Publish the app outside of local machine so it can run with minimal manual setup. Tools: GitHub Actions, Posit Connect, Docker. Deliverable: Deployable app with setup instructions. Keywords: deployment, hosting, workflow, automation, production.
4. **Custom RAG Prototype**: Search project records before sending context to the model for grounded answers. Tools: Python, pandas, Ollama. Deliverable: RAG script and output screenshot. Keywords: rag, retrieval, context, grounded, search.
5. **Final Project Report**: Combine code results and narrative explanation into a polished deliverable for submission. Tools: Markdown, HTML, DOCX. Deliverable: Final report package and presentation notes. Keywords: report, summary, deliverable, writeup, presentation. 

This project meets its goals using the provided tools and components, but there is an incomplete section regarding how to implement the custom RAG prototype within the given context and timeframe.
