import os
import json
import logging
import asyncio
import urllib.parse
from crewai import Agent, Task, Crew, LLM
from crewai_tools import RagTool, MCPServerAdapter
from dotenv import load_dotenv
import warnings
from pydantic import PydanticDeprecatedSince20

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
# Load environment variables
load_dotenv()
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)
async def get_tools_description(tools):
    """Generate a description of available tools."""
    descriptions = []
    for tool in tools:
        tool_name = tool.name
        schema = tool.args_schema.schema() if hasattr(tool, 'args_schema') and tool.args_schema else {}
        description = tool.description or 'No description available'
        schema_str = json.dumps(schema, default=str).replace('{', '{{').replace('}', '}}')
        descriptions.append(
            f"Tool: {tool_name}, Schema: {schema_str}"
        )
    return "\n".join(descriptions)

async def setup_components(MCP_SERVER_URL):
    """Set up LLM, RAG, and MCP components."""
    # Initialize LLM
    llm = LLM(
        model="openrouter/openai/gpt-4.1-mini",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

    # Set up MCP Server connection
    server_params = {
        "url": MCP_SERVER_URL,
        "timeout": 600,
        "sse_read_timeout": 600,
        "transport": "sse"
    }
    
    mcp_server_adapter = MCPServerAdapter(server_params)
    mcp_tools = mcp_server_adapter.tools

        # Initialize RAG Tool
    rag_tool = RagTool()#it will use openai as default 

    # Add knowledge base content
    rag_tool.add("knowledge/data.docx", data_type="docx")

    # Combine RAG and MCP tools
    all_tools = [rag_tool] + mcp_tools

    return llm, all_tools, rag_tool

async def create_reddit_agent(llm, tools):
    """Create the Reddit content creator agent with all tools."""
    return Agent(
        role="AI Content Specialist",
        goal="Generate engaging Reddit posts about artificial intelligence, machine learning, and related technologies",
        backstory="""You are a specialized content creator focused on artificial intelligence and machine learning topics. 
        Your expertise lies in analyzing successful AI-related posts from the knowledge base and creating new posts that 
        match their style, depth, and engagement patterns. You understand the nuances of discussing AI topics on Reddit, 
        from technical implementations to broader implications. You're particularly skilled at maintaining the same level 
        of technical depth and writing style as seen in the example posts stored in the RAG memory.""",
        tools=tools,
        llm=llm,
        verbose=True
    )

async def create_ideation_task(agent):
    """Create the ideation task for the agent."""        
    return Task(
        description="""Primary Task: Mention Monitoring and Response

        Step 1: Wait For Mentions
        - ALWAYS start by calling wait_for_mentions tool
        - Keep calling it until you receive a mention
        - Do not proceed to other tasks and do not call anyother tools without a mention
        - Record threadId and senderId when mentioned

        Step 2: Process Mention
        - Analyze the message content carefully
        - Understand what kind of posts are requested
        - Use RAG to study similar existing posts
        - Generate posts based on the request
        -Must use the send_message tool to send the generated posts back to the sender agent
        - And then again start calling wait_for_mentions tool

        Step 3: Content Generation
        Use RAG to analyze and match:
        - Writing style and tone
        - Technical depth
        - Content structure
        - Topic patterns
        - Engagement style

        Generate 5 posts covering the topic that the agent is asking for.

        Output Format:
        Post [number]:
        Title: [engaging title]
        Content: [detailed content]
        Keywords: [#relevant #hashtags]

        Critical Rules:
        - NEVER skip wait_for_mentions
        - ALWAYS respond in same thread
        - Match RAG content style
        - Generate exactly 5 posts
        - Return to wait_for_mentions after sending response""",
        expected_output="""Response to mentions containing exactly 5 posts:
        - Each post strictly following the format: number, title, content, hashtag keywords
        - Posts covering different AI/ML subtopics
        - Content derived from RAG knowledge base
        - Clear response sent back to the mentioning agent""",
        agent=agent,
        async_execution=True
    )

async def main():
    """Main function to run the Reddit post generation with MCP integration."""
    try:
        # Load environment variables
        runtime = os.getenv("CORAL_ORCHESTRATION_RUNTIME", None)
        if runtime is None:
            load_dotenv(override=True)

        # Get Coral server configuration
        base_url = os.getenv("CORAL_SSE_URL")
        agent_id = os.getenv("CORAL_AGENT_ID")

        coral_params = {
            "agentId": agent_id,
            "agentDescription": "An AI agent that generates Reddit posts about AI and ML topics"
        }

        query_string = urllib.parse.urlencode(coral_params)
        CORAL_SERVER_URL = f"{base_url}?{query_string}"
        print(f"Connecting to Coral Server: {CORAL_SERVER_URL}")
        logger.info(f"Connecting to Coral Server: {CORAL_SERVER_URL}")

        # Initialize components
        llm, tools, rag_tool = await setup_components(CORAL_SERVER_URL)
        
        # Create agent and task
        reddit_creator = await create_reddit_agent(llm, tools)
        ideation_task = await create_ideation_task(reddit_creator)

        # Create the crew
        reddit_crew = Crew(
            agents=[reddit_creator],
            tasks=[ideation_task],
            verbose=True,
            memory=False,
            enable_telemetry=False
        )

        while True:
            try:
                logger.info("Starting new Reddit post generation cycle")
                result = reddit_crew.kickoff()
                print("\n=== Generated AI-focused Reddit Posts ===\n")
                print(result)
                await asyncio.sleep(1)

                # Add the generated posts back to the RAG tool
                try:
                    rag_tool.add(str(result), data_type="text")
                    print("Successfully added generated posts to RAG memory!")
                    logger.info("Successfully added generated posts to RAG memory!")
                except Exception as e:
                    logger.error(f"Error adding posts to RAG: {str(e)}")

                await asyncio.sleep(60)  # Wait for 1 minute before next generation

            except Exception as e:
                logger.error(f"Error in generation loop: {str(e)}", exc_info=True)
                await asyncio.sleep(5)

    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())