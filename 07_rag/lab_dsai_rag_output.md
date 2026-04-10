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
Title: Building a Project Dashboard for Non-Technical Users

Summary:
This project involves creating an interactive dashboard that summarizes project metrics for non-technical users. The goal is to make it easy for them to understand and track progress without requiring technical expertise.

Relevant Components:

1. **Interactive Dashboard**: This component uses Shiny to create a visually appealing, user-friendly interface where key statistics can be explored in real-time. It also includes an option for users to filter by project stage or specific milestones.
   
2. **Summary Report**: A concise report generated from the data collected from the dashboard will provide a comprehensive overview of project performance over time. The report can be delivered in HTML format making it easy to share with stakeholders and team members.

3. **Document Visualization**: To complement the interactive elements, we can also visualize our project documents using Python or RAG (Rapid Answer Generator). This tool uses machine learning algorithms to provide quick answers when a user asks a question based on their context information provided through previous interactions.

4. **LML and Prompt Engineering**: These tools are part of the "AI Query Assistant" topic mentioned above but are crucial for making the system work effectively. They enable us to generate relevant responses from our project records when asked questions, ensuring answers stay grounded in factual data.

5. **GitHub Actions, Posit Connect, Docker** - The delivery instructions for the deployment workflow provide information on how these tools can be used for automating tasks and ensuring the app is hosted outside the local machine with minimal setup requirements.
