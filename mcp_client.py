import asyncio
import sys
import json
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from llmModel import llm

async def run_client():
    print("--- Conectando ao Servidor MCP (Versão FastMCP 3.0 + LangChain) ---")
    
    # Define o transporte STDIO explicitamente para o FastMCP 3.0
    transport = StdioTransport(command=sys.executable, args=["mcp_server.py"])
    
    async with Client(transport) as client:
        # 1. Lista as ferramentas e prompts disponíveis no servidor
        mcp_tools = await client.list_tools()
        
        # 2. Transforma ferramentas MCP em ferramentas LangChain
        langchain_tools = []
        
        def create_tool_wrapper(tool_name):
            async def _mcp_tool_wrapper(tool_input):
                try:
                    actual_args = json.loads(tool_input) if isinstance(tool_input, str) else tool_input
                except:
                    actual_args = tool_input

                print(f"\n[DEBUG] IA chamando ferramenta '{tool_name}' com: {actual_args}")
                
                if not isinstance(actual_args, dict):
                     actual_args = {"input": actual_args}

                # O client do FastMCP permite chamar ferramentas diretamente
                result = await client.call_tool(tool_name, actual_args)
                # O resultado do FastMCP 3.0 pode ser acessado de forma mais direta
                content = "\n".join([c.text for c in result.content if hasattr(c, 'text')])
                
                print(f"[DEBUG] Resposta do MCP para '{tool_name}': {content}")
                return content
            return _mcp_tool_wrapper

        for tool in mcp_tools:
            lc_tool = Tool(
                name=tool.name,
                func=None,
                coroutine=create_tool_wrapper(tool.name),
                description=tool.description
            )
            langchain_tools.append(lc_tool)

        # 2.2 Suporte a Prompts MCP
        try:
            mcp_prompts = await client.list_prompts()
            for p in mcp_prompts:
                def create_prompt_wrapper(p_name):
                    async def _lc_prompt_wrapper(p_input):
                        try:
                            args = json.loads(p_input) if isinstance(p_input, str) else p_input
                        except:
                            args = {"tema": p_input} if "sugestao" in p_name else {}
                        
                        res = await client.get_prompt(p_name, args)
                        return "\n".join([m.content.text for m in res.messages if hasattr(m.content, 'text')])
                    return _lc_prompt_wrapper

                prompt_tool = Tool(
                    name=f"obter_prompt_{p.name}",
                    func=None,
                    coroutine=create_prompt_wrapper(p.name),
                    description=f"Template de suporte: {p.description}"
                )
                langchain_tools.append(prompt_tool)
        except Exception as e:
            print(f"[Aviso] Não foi possível carregar prompts: {e}")

        # 3. Agente LangChain (ReAct)
        template = """Você é um assistente de gerenciamento de tarefas para Django/PostgreSQL.
Responda sempre em Português e seja breve.

Ferramentas disponíveis:
{tools}

Regras:
1. Se uma ferramenta exige informações que o usuário não forneceu, pergunte antes de agir.
2. Use 'obter_prompt_sugestao_tarefa' para ideias.
3. Se criar uma tarefa, use 'obter_prompt_formato_conclusao_tarefa' para anunciar.

Formato de Resposta:
Question: a pergunta do usuário
Thought: o seu raciocínio sobre o que fazer
Action: a ferramenta a ser usada (deve ser uma de [{tool_names}])
Action Input: a entrada para a ferramenta (em formato JSON se houver múltiplos campos)
Observation: o resultado da ferramenta
... (Thought/Action/Action Input/Observation podem se repetir)
Thought: Eu sei a resposta final
Final Answer: a resposta final para o usuário

Question: {input}
{agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)
        agent = create_react_agent(llm, langchain_tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent, 
            tools=langchain_tools, 
            verbose=True, 
            handle_parsing_errors=True,
            max_iterations=5 # Proteção contra loops infinitos
        )

        print("--- Cliente FastMCP + LangChain Pronto! ---")
        print("(Digite 'sair' para encerrar)\n")

        while True:
            user_input = await asyncio.get_event_loop().run_in_executor(None, input, "Você: ")
            
            if user_input.lower() in ["sair", "exit", "quit"]:
                break
            
            try:
                response = await agent_executor.ainvoke({"input": user_input})
                print(f"\nIA: {response['output']}\n")
            except Exception as e:
                print(f"\nErro no Agente: {e}\n")

if __name__ == "__main__":
    asyncio.run(run_client())

if __name__ == "__main__":
    asyncio.run(run_client())
