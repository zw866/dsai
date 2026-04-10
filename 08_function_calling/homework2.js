const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, PageBreak, LevelFormat, ExternalHyperlink, ImageRun
} = require("docx");

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

function headerCell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: "2E4057", type: ShadingType.CLEAR },
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })]
  });
}

function cell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, font: "Arial", size: 20 })] })]
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: "2E4057" },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "2E4057" },
        paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "3A5A7C" },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "bullets2",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "bullets3",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "bullets4",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers1",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      // ==================== TITLE ====================
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 100 },
        children: [new TextRun({ text: "Homework 2: AI Agent System with RAG and Tools", bold: true, size: 40, font: "Arial", color: "2E4057" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 100 },
        children: [new TextRun({ text: "SYSEN 5381: Data Science and AI for Systems Engineering", size: 24, font: "Arial", color: "555555" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 400 },
        children: [new TextRun({ text: "Jack Wen", size: 24, font: "Arial" })]
      }),

      // ==================== SECTION 1: WRITING ====================
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. System Overview (Writing Component)")] }),

      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun({ text: "[NOTE: This section must be rewritten in your own words before submission. The following is a draft for reference.]", italics: true, color: "CC0000", size: 20 })]
      }),

      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun(
          "My system combines three components: multi-agent orchestration, RAG, and function calling. Multiple AI agents work together in a chain, each handling one step of a task and passing its output to the next agent."
        )]
      }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun(
          "In Week 1, I built a 3-agent workflow for FDA drug shortage analysis: Agent 1 parses the data, Agent 2 assesses risk, and Agent 3 writes a summary. In Week 2, I implemented RAG by searching a custom CSV file (dsai_project_notes.csv) with keyword matching and feeding the results as context to the LLM for grounded answers."
        )]
      }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun(
          "In Week 3, I added function calling with a get_world_bank_data() tool that fetches GDP data from the World Bank API. Agent 1 calls the tool, Agent 2 analyzes the data. The main challenge was that smollm2:1.7b sometimes fails to generate tool calls, so I added a fallback that calls the function directly."
        )]
      }),

      // ==================== SECTION 2: CODE LINKS ====================
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Code Repository Links")] }),

      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun({ text: "GitHub Repository: ", bold: true }),]
      }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new ExternalHyperlink({
          children: [new TextRun({ text: "https://github.com/zw866/dsai", style: "Hyperlink" })],
          link: "https://github.com/zw866/dsai"
        })]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Multi-Agent Orchestration")] }),
      new Paragraph({
        spacing: { after: 80 },
        numbering: { reference: "bullets", level: 0 },
        children: [new ExternalHyperlink({
          children: [new TextRun({ text: "06_agents/lab_multi_agent.py", style: "Hyperlink" })],
          link: "https://github.com/zw866/dsai/blob/main/06_agents/lab_multi_agent.py"
        }), new TextRun(" - 3-agent drug shortage analysis workflow")]
      }),
      new Paragraph({
        spacing: { after: 200 },
        numbering: { reference: "bullets", level: 0 },
        children: [new ExternalHyperlink({
          children: [new TextRun({ text: "06_agents/functions.py", style: "Hyperlink" })],
          link: "https://github.com/zw866/dsai/blob/main/06_agents/functions.py"
        }), new TextRun(" - Agent helper functions (agent_run, get_shortages, df_as_text)")]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("RAG Implementation")] }),
      new Paragraph({
        spacing: { after: 80 },
        numbering: { reference: "bullets2", level: 0 },
        children: [new ExternalHyperlink({
          children: [new TextRun({ text: "07_rag/lab_dsai_rag.py", style: "Hyperlink" })],
          link: "https://github.com/zw866/dsai/blob/main/07_rag/lab_dsai_rag.py"
        }), new TextRun(" - RAG query script with search function")]
      }),
      new Paragraph({
        spacing: { after: 80 },
        numbering: { reference: "bullets2", level: 0 },
        children: [new ExternalHyperlink({
          children: [new TextRun({ text: "07_rag/data/dsai_project_notes.csv", style: "Hyperlink" })],
          link: "https://github.com/zw866/dsai/blob/main/07_rag/data/dsai_project_notes.csv"
        }), new TextRun(" - Custom RAG data source")]
      }),
      new Paragraph({
        spacing: { after: 200 },
        numbering: { reference: "bullets2", level: 0 },
        children: [new ExternalHyperlink({
          children: [new TextRun({ text: "07_rag/lab_dsai_rag_output.md", style: "Hyperlink" })],
          link: "https://github.com/zw866/dsai/blob/main/07_rag/lab_dsai_rag_output.md"
        }), new TextRun(" - RAG output results")]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Function Calling / Tool Definitions")] }),
      new Paragraph({
        spacing: { after: 80 },
        numbering: { reference: "bullets3", level: 0 },
        children: [new ExternalHyperlink({
          children: [new TextRun({ text: "08_function_calling/lab_multi_agent_with_tools.py", style: "Hyperlink" })],
          link: "https://github.com/zw866/dsai/blob/main/08_function_calling/lab_multi_agent_with_tools.py"
        }), new TextRun(" - 2-agent workflow with World Bank API tool")]
      }),
      new Paragraph({
        spacing: { after: 200 },
        numbering: { reference: "bullets3", level: 0 },
        children: [new ExternalHyperlink({
          children: [new TextRun({ text: "08_function_calling/functions.py", style: "Hyperlink" })],
          link: "https://github.com/zw866/dsai/blob/main/08_function_calling/functions.py"
        }), new TextRun(" - Agent and tool execution functions")]
      }),

      // ==================== SECTION 3: SCREENSHOTS ====================
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Screenshots and Outputs")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Screenshot 1: Multi-Agent Workflow (06_agents)")] }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Shows 3-agent pipeline: Data Analyst \u2192 Risk Assessor \u2192 Report Writer analyzing FDA drug shortage data.")]
      }),
      new Paragraph({
        spacing: { after: 300 },
        children: [new ImageRun({
          type: "png",
          data: fs.readFileSync("/Users/jackwen/Desktop/截屏2026-03-29 下午4.04.15.png"),
          transformation: { width: 580, height: 340 },
          altText: { title: "Multi-Agent", description: "Multi-agent workflow output", name: "screenshot1" }
        })]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Screenshot 2: RAG Retrieval (07_rag)")] }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Shows keyword search retrieving 5 matching records from dsai_project_notes.csv.")]
      }),
      new Paragraph({
        spacing: { after: 300 },
        children: [new ImageRun({
          type: "png",
          data: fs.readFileSync("/Users/jackwen/Desktop/截屏2026-03-29 下午4.04.24.png"),
          transformation: { width: 580, height: 340 },
          altText: { title: "RAG Search", description: "RAG search results", name: "screenshot2" }
        })]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Screenshot 3: RAG Response (07_rag)")] }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("LLM-generated response grounded in retrieved context.")]
      }),
      new Paragraph({
        spacing: { after: 300 },
        children: [new ImageRun({
          type: "png",
          data: fs.readFileSync("/Users/jackwen/Desktop/截屏2026-03-29 下午4.04.35.png"),
          transformation: { width: 580, height: 340 },
          altText: { title: "RAG Response", description: "RAG generated response", name: "screenshot3" }
        })]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Screenshot 4: Function Calling with World Bank API (08_function_calling)")] }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Agent 1 calls get_world_bank_data() tool to fetch China GDP data, Agent 2 generates trend analysis report.")]
      }),
      new Paragraph({
        spacing: { after: 300 },
        children: [new ImageRun({
          type: "png",
          data: fs.readFileSync("/Users/jackwen/Desktop/截屏2026-03-29 下午4.05.07.png"),
          transformation: { width: 580, height: 340 },
          altText: { title: "Function Calling", description: "Function calling workflow output", name: "screenshot4" }
        })]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Screenshot 5: MCP Server Tool Call (08_function_calling)")] }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("calculate_bmi tool called via MCP HTTP endpoint, returning BMI value and WHO category.")]
      }),
      new Paragraph({
        spacing: { after: 300 },
        children: [new ImageRun({
          type: "png",
          data: fs.readFileSync("/Users/jackwen/Desktop/截屏2026-03-29 下午3.32.23.png"),
          transformation: { width: 580, height: 340 },
          altText: { title: "MCP Server", description: "MCP server tool call", name: "screenshot6" }
        })]
      }),

      // ==================== SECTION 4: DOCUMENTATION ====================
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Documentation")] }),

      // System Architecture
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 System Architecture")] }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun("The system consists of three integrated components, each built as a separate module:")]
      }),

      new Paragraph({
        spacing: { after: 80 },
        children: [new TextRun({ text: "Component 1: Multi-Agent Drug Shortage Analysis (06_agents)", bold: true })]
      }),
      new Paragraph({
        spacing: { after: 40 },
        numbering: { reference: "bullets4", level: 0 },
        children: [new TextRun({ text: "Agent 1 (Data Analyst): ", bold: true }), new TextRun("Parses raw FDA drug shortage data, counts unavailable drugs, groups by therapeutic category")]
      }),
      new Paragraph({
        spacing: { after: 40 },
        numbering: { reference: "bullets4", level: 0 },
        children: [new TextRun({ text: "Agent 2 (Risk Assessor): ", bold: true }), new TextRun("Evaluates severity (Low/Medium/High), identifies affected patient populations, suggests hospital actions")]
      }),
      new Paragraph({
        spacing: { after: 200 },
        numbering: { reference: "bullets4", level: 0 },
        children: [new TextRun({ text: "Agent 3 (Report Writer): ", bold: true }), new TextRun("Produces executive summary with Current Situation, Risk Level, and Recommended Actions")]
      }),

      new Paragraph({
        spacing: { after: 80 },
        children: [new TextRun({ text: "Component 2: RAG Query System (07_rag)", bold: true })]
      }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun("Single agent with retrieval: search_project_notes() searches dsai_project_notes.csv using keyword matching across topic, goal, tools, deliverable, and keywords columns. Matched records are passed as JSON context to the LLM for grounded responses.")]
      }),

      new Paragraph({
        spacing: { after: 80 },
        children: [new TextRun({ text: "Component 3: Function Calling Workflow (08_function_calling)", bold: true })]
      }),
      new Paragraph({
        spacing: { after: 300 },
        children: [new TextRun("Two-agent pipeline: Agent 1 (Data Fetcher) uses get_world_bank_data() tool to call the World Bank API and retrieve economic indicators. Agent 2 (Report Writer) receives the data as a markdown table and generates a trend analysis report.")]
      }),

      // RAG Data Source
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.2 RAG Data Source")] }),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2340, 7020],
        rows: [
          new TableRow({ children: [headerCell("Property", 2340), headerCell("Details", 7020)] }),
          new TableRow({ children: [cell("File", 2340), cell("07_rag/data/dsai_project_notes.csv", 7020)] }),
          new TableRow({ children: [cell("Records", 2340), cell("8 project records", 7020)] }),
          new TableRow({ children: [cell("Columns", 2340), cell("id, topic, goal, tools, deliverable, keywords", 7020)] }),
          new TableRow({ children: [cell("Search Method", 2340), cell("Keyword matching: splits query into terms (4+ chars), searches across all text columns", 7020)] }),
          new TableRow({ children: [cell("Search Function", 2340), cell("search_project_notes(query, document_path, limit=5)", 7020)] }),
          new TableRow({ children: [cell("Return Format", 2340), cell("JSON with query, document name, matched records, and match count", 7020)] }),
        ]
      }),

      new Paragraph({ spacing: { after: 300 }, children: [] }),

      // Tool Functions
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.3 Tool Functions")] }),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [1800, 2200, 2700, 2660],
        rows: [
          new TableRow({ children: [
            headerCell("Tool Name", 1800), headerCell("Purpose", 2200), headerCell("Parameters", 2700), headerCell("Returns", 2660)
          ]}),
          new TableRow({ children: [
            cell("get_shortages", 1800),
            cell("Fetch drug shortage data from FDA API", 2200),
            cell("category (str): therapeutic category; limit (int): max results", 2700),
            cell("DataFrame with generic_name, update_type, update_date, availability", 2660)
          ]}),
          new TableRow({ children: [
            cell("get_world_bank_data", 1800),
            cell("Fetch economic indicators from World Bank API", 2200),
            cell("country (str): ISO country code; indicator (str): WB indicator code", 2700),
            cell("DataFrame with year, country, indicator, value", 2660)
          ]}),
          new TableRow({ children: [
            cell("search_project_notes", 1800),
            cell("Search CSV records by keyword matching for RAG", 2200),
            cell("query (str): search text; document_path (str): CSV path; limit (int): max results", 2700),
            cell("Dict with query, document, matches list, num_matches", 2660)
          ]}),
          new TableRow({ children: [
            cell("calculate_bmi", 1800),
            cell("Calculate BMI via MCP server endpoint", 2200),
            cell("weight_kg (float): weight in kg; height_m (float): height in meters", 2700),
            cell("JSON with bmi value, WHO category, inputs", 2660)
          ]}),
        ]
      }),

      new Paragraph({ spacing: { after: 300 }, children: [] }),

      // Technical Details
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.4 Technical Details")] }),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2800, 6560],
        rows: [
          new TableRow({ children: [headerCell("Item", 2800), headerCell("Details", 6560)] }),
          new TableRow({ children: [cell("LLM", 2800), cell("Ollama with smollm2:1.7b (local, port 11434)", 6560)] }),
          new TableRow({ children: [cell("Language", 2800), cell("Python 3.13", 6560)] }),
          new TableRow({ children: [cell("Key Packages", 2800), cell("requests, pandas, json, fastapi, uvicorn", 6560)] }),
          new TableRow({ children: [cell("External APIs", 2800), cell("World Bank API (api.worldbank.org), FDA Drug Shortages API (api.fda.gov)", 6560)] }),
          new TableRow({ children: [cell("MCP Server", 2800), cell("FastAPI-based, runs on localhost:8000, JSON-RPC protocol", 6560)] }),
          new TableRow({ children: [cell("API Keys Required", 2800), cell("None (all APIs used are public and free)", 6560)] }),
        ]
      }),

      new Paragraph({ spacing: { after: 300 }, children: [] }),

      // Usage Instructions
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.5 Usage Instructions")] }),

      new Paragraph({
        spacing: { after: 80 },
        children: [new TextRun({ text: "Prerequisites:", bold: true })]
      }),
      new Paragraph({
        spacing: { after: 200 },
        numbering: { reference: "numbers1", level: 0 },
        children: [new TextRun("Install Ollama and pull the model: "), new TextRun({ text: "ollama pull smollm2:1.7b", bold: true })]
      }),
      new Paragraph({
        spacing: { after: 200 },
        numbering: { reference: "numbers1", level: 0 },
        children: [new TextRun("Install Python packages: "), new TextRun({ text: "pip install requests pandas fastapi uvicorn tabulate", bold: true })]
      }),

      new Paragraph({
        spacing: { after: 80 },
        children: [new TextRun({ text: "Running each component:", bold: true })]
      }),
      new Paragraph({
        spacing: { after: 200 },
        numbering: { reference: "numbers1", level: 0 },
        children: [new TextRun({ text: "Multi-Agent (06_agents): ", bold: true }), new TextRun("python3 06_agents/lab_multi_agent.py")]
      }),
      new Paragraph({
        spacing: { after: 200 },
        numbering: { reference: "numbers1", level: 0 },
        children: [new TextRun({ text: "RAG (07_rag): ", bold: true }), new TextRun("python3 07_rag/lab_dsai_rag.py")]
      }),
      new Paragraph({
        spacing: { after: 200 },
        numbering: { reference: "numbers1", level: 0 },
        children: [new TextRun({ text: "Function Calling (08_function_calling): ", bold: true }), new TextRun("python3 08_function_calling/lab_multi_agent_with_tools.py")]
      }),
      new Paragraph({
        spacing: { after: 200 },
        numbering: { reference: "numbers1", level: 0 },
        children: [new TextRun({ text: "MCP Server (08_function_calling): ", bold: true }), new TextRun("cd 08_function_calling/mcp_fastapi && python3 -m uvicorn server:app --port 8000")]
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/Users/jackwen/Desktop/5381/dsai/08_function_calling/homework2.docx", buffer);
  console.log("homework2.docx created successfully");
});
