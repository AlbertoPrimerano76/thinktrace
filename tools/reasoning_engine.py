import asyncio
import os
from typing import AsyncGenerator, Dict, Any
from core import logger,config_manager,load_simulation_prompt,extract_json_from_response
from .ollama_mcp_client import OllamaAgent



def serialize_response(obj):
    """Recursively convert an object into a JSON-serializable form."""
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    if isinstance(obj, dict):
        return {k: serialize_response(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [serialize_response(i) for i in obj]
    if hasattr(obj, "model_dump"):  # Pydantic model
        return serialize_response(obj.model_dump())
    if hasattr(obj, "__dict__"):  # General object
        return serialize_response(vars(obj))
    if hasattr(obj, "__str__"):  # Fallback to string
        return str(obj)
    return f"<<Unserializable: {type(obj).__name__}>>"

def sanitize_reasoning_steps(steps):
    return [
        step for step in steps
        if step.get("description") is not None and step.get("step_id")
    ]

def extract_text_from_serialized_result(serialized_result: dict) -> str:
    try:
        content_list = serialized_result.get("output", {}).get("content", [])
        # Unisci solo i testi dei blocchi di tipo 'text'
        texts = [item["text"] for item in content_list if item.get("type") == "text"]
        return "\n".join(texts)
    except Exception as e:
        logger.error(f"Error extracting text from serialized results :\n{e}")
        return "[Error extracting text]"




# 🚀 Main reasoning pipeline
async def run_reasoning_pipeline(user_question: str, llm_agent: OllamaAgent, top_k: float, top_p: float, temperature: float) -> AsyncGenerator[Dict[str, Any], None]:
    reasoning_state = {"question": user_question, "model": llm_agent.model}
    results = {}

    try:
        #
        # 1. Generating reasoning prompt
        #
        reasoning_prompt = f"Generating reasoning prompt for: {user_question}"
        reasoning_state["reasoning_prompt"] = reasoning_prompt
        yield { "chat": "🚀 Generating Reasoning Prompt...", 
                "debug": 
                    {   "step": 1, 
                        "title": "Setting up", 
                        "emoji" : "🚀",
                        "css_class" : "generation-step",
                        "rendered_prompt": reasoning_prompt
                    }
                }
        path = os.path.join(config_manager.CONFIG_FOLDER_PATH, config_manager.PROMPT_FILE_NAME)
        prompt_template = load_simulation_prompt(path)
        
        
        if llm_agent.tools:
            available_tools = "\n".join(
                f"{tool['function']['name']} : {tool['function']['description']}"
                for tool in llm_agent.tools
            )
        else:
            available_tools = "No tools available at this time."

            
        if "{{ user_input }}" not in prompt_template:
            raise ValueError("Reasoning prompt template missing '{{ user_input }}' placeholder.")

        if "{{ available_tools }}" not in prompt_template:
            raise ValueError("Reasoning prompt template missing '{{ available_tools }}' placeholder.")
        
        reasoning_prompt = prompt_template.replace("{{ user_input }}", user_question)
        reasoning_prompt = reasoning_prompt.replace("{{ available_tools }}", available_tools)



        logger.debug(f"Prepared reasoning prompt:\n{reasoning_prompt}")
        
        reasoning_state["reasoning_prompt"] = reasoning_prompt
        
        await asyncio.sleep(1)
        
        yield   {   "chat": "✅ Reasoning prompt generated successfully.", 
                    "debug": 
                        {
                            "step": 1, 
                            "title": "Prompt Ready", 
                            "emoji" : "✅",
                            "css_class" : "generation-step",
                            "rendered_prompt": reasoning_prompt
                        }
            }
            
        await asyncio.sleep(1)

        #
        # 2. Generating reasoning plan using LLM (ollama)
        #
        messages = [
                {"role": "system", "content": "You simulate step-by-step reasoning like an LLM would internally."},
                {"role": "user", "content": reasoning_prompt}
            ]

        yield   {   "chat": "🧠 Generating reasoning plan ...", 
                    "debug": 
                        {
                            "step": 2, 
                            "title": "Generating Reasoning Plan", 
                            "emoji" : "🧠",
                            "css_class" : "generation-step",
                            "messages": messages
                        }
                }

        await asyncio.sleep(1)
   
        try:
            raw_response = await llm_agent.run(messages=messages, add_tools=False)
            response = extract_json_from_response(raw_response)

            response = {
                **response,
                "reasoning_steps": sanitize_reasoning_steps(response.get("reasoning_steps", []))
            }
            reasoning_state["generated_plan"] = response
            yield   {   "chat": "✅ Reasoning plan generated successfully.", 
                        "debug": 
                            {
                                "step": 2, 
                                "title": "Reasoning Plan Generated",
                                "emoji" : "✅",
                                "css_class" : "generation-step", 
                                "reasoning": response
                            }
                    }
            
            await asyncio.sleep(1)

        except Exception as e:
            logger.error("Failed to generate reasoning plan after retries.", exc_info=True)
            yield   {   "chat": "❌ Failed to generate reasoning plan.", 
                        "debug": 
                            {   "step": "Error", 
                                "title": "Plan Generation Failed", 
                                "emoji" : "❌",
                                "css_class" : "error-step", 
                                "error": str(e)
                            
                            }
                    }
            return

        #
        # 3. Execute reasoning steps using LLM (ollama)
        #
        
        steps = reasoning_state["generated_plan"].get("reasoning_steps", [])
        results = {}
        count_steps = 2
        for step_index, step in enumerate(steps, start=3):
            
            step_id = step["step_id"]
            description = step["description"]
            type=step["step_type"]
            dependencies = step.get("dependencies", [])
        
            # Get dependency outputs
            dep_results = [
                extract_text_from_serialized_result(results[d])
                for d in dependencies if d in results
            ]
            context = "\n".join(dep_results)
            
            messages = [
                {"role": "system", "content": f"You are an LLM agent that should execute the following task: {description} in order to provide context for the following steps of the reasoning process defined to answer the customer question."},
                {"role": "system", "content": f"Previous steps from from the process provided you the following context: {context} "},
                {"role": "user", "content": f"The user original question is {user_question}"}
            ]
            
            emoji = "🛠️" if step["step_type"] == "tool_use" else "🧠"
            yield {
                    "chat": f"{emoji} Executing Reasoning step {step_index}: {description}",
                    "debug": {
                        "step": step_index,
                        "title": "Executing reasoning step",
                        "emoji": emoji,
                        "type" : type,
                        "description" : description,
                        "messages": messages
                    }
                }
            
            await asyncio.sleep(1)
            
            add_tools = step["step_type"] == "tool_use"
            try:
                raw_response = await llm_agent.run(messages=messages, add_tools=add_tools)
                logger.info(f"✅ Raw response: {raw_response}")
                results[step_id] = serialize_response(raw_response)    

                yield {
                    "chat": f"✅ Reasoning step {step_index} executed.",
                    "debug": {
                        "step": step_index,
                        "title": "Reasoning step executed",
                        "type": type,
                        "emoji" : "✅",
                        "css_class" : "generation-step", 
                        "output": serialize_response(raw_response)
                    }
                }

                await asyncio.sleep(1)

                count_steps = count_steps + 1
            except Exception as e:
                logger.error("Failed to generate reasoning plan after retries.", exc_info=True)
                yield   {   "chat": "❌ Failed to execute reasoning step.", 
                            "debug": 
                                {   "step": "Error", 
                                    "title": "Execution Step Failed", 
                                    "emoji" : "❌",
                                    "css_class" : "error-step", 
                                    "error": str(e)
                                
                                }
                        }
                return        

        # Final reasoning summary prompt


        messages = [
                {"role": "system", "content": "You are an LLM agent that should provide an answer to a question."},
                {"role": "system", "content": f"To answer the question you can use the following context {results} "},
                {"role": "user", "content": f"The user original question is {user_question} provide just the answer to the quesiton."}
            ]
        
        
        yield {
                "chat": "🧠 Wrapping up and generating final answer",
                "debug": {
                    "step": count_steps + 1,
                    "title": "Wrapping up and generating final answer",
                    "emoji" : "🧠",
                    "css_class" : "generation-step",
                    "messages" : messages
                }
            }
            
        await asyncio.sleep(1)
        
        
        try:
            final_answer = await llm_agent.run(messages=messages, add_tools=False)
        except Exception as e:
                logger.error("Failed to generate the final answer", exc_info=True)
                yield   {   "chat": "❌ Failed to execute final answer generation step.", 
                            "debug": 
                                {   "step": "Error", 
                                    "title": "Final answer generation step Failed", 
                                    "emoji" : "❌",
                                    "css_class" : "error-step", 
                                    "error": str(e)
                                
                                }
                        }
                return        
        
        yield {
            "chat": final_answer,
            "debug": {
                "step": count_steps + 1,
                "title": "Final Reasoning Result",
                "emoji" : "✅",
                "css_class" : "generation-step",
                "final_answer": final_answer
            }
        }
   
    except Exception as e:
        logger.exception("Fatal error in pipeline.")
        yield {"chat": "❌ A fatal error occurred in the process.", "debug": {"step": "fatal", "error": str(e)}}
