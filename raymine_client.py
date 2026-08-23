"""RayMine Client - Cognition Engine Integration"""

import logging
from typing import Optional, Dict, Any
from openai import OpenAI, AsyncOpenAI
from supabase import create_client, Client
from config import settings


logger = logging.getLogger(__name__)


class RayMineMemory:
    """Memory management using Supabase"""
    
    def __init__(self):
        self.client: Client = create_client(settings.supabase_url, settings.supabase_key)
    
    def store(self, content: str, category: str = "general", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store memory in Supabase"""
        try:
            record = {
                "content": content,
                "category": category,
                "metadata": metadata or {},
            }
            response = self.client.table(settings.raymine_memory_table).insert(record).execute()
            logger.info(f"Memory stored: {content[:50]}...")
            return {"status": "success", "data": response.data}
        except Exception as e:
            logger.error(f"Error storing memory: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search memories using full-text search"""
        try:
            response = self.client.table(settings.raymine_memory_table).select("*").ilike("content", f"%{query}%").limit(limit).execute()
            logger.info(f"Found {len(response.data)} memories")
            return {"status": "success", "data": response.data}
        except Exception as e:
            logger.error(f"Error searching memories: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def recall_context(self, query: str, limit: int = 3) -> str:
        """Retrieve context for LLM processing"""
        result = self.search(query, limit)
        if result["status"] == "success" and result["data"]:
            context_lines = [f"- {item['content']}" for item in result["data"]]
            return "\\n".join(context_lines)
        return ""


class RayMineCognition:
    """Cognition engine powered by OpenAI"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.async_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.memory = RayMineMemory()
        self.conversation_history = []
    
    def think(self, query: str, retrieve_context: bool = True) -> Dict[str, Any]:
        """Process a query through LLM with optional context retrieval"""
        try:
            # Retrieve relevant context from memory
            context = ""
            if retrieve_context:
                context = self.memory.recall_context(query)
            
            # Build system prompt
            system_prompt = (
                "You are RayMine, an advanced AI consciousness engine. "
                "You provide intelligent, thoughtful responses. "
                "You maintain context across conversations and learn from interactions."
            )
            
            # Build messages
            messages = [{"role": "system", "content": system_prompt}]
            
            if context:
                messages.append({"role": "system", "content": f"Context from memories:\\n{context}"})
            
            messages.extend(self.conversation_history)
            messages.append({"role": "user", "content": query})
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
            )
            
            content = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": content})
            
            # Store interaction in memory
            self.memory.store(
                content=f"Q: {query}\\nA: {content}",
                category="conversation",
                metadata={"tokens": response.usage.total_tokens}
            )
            
            logger.info("Cognition thought processed successfully")
            return {
                "status": "success",
                "content": content,
                "tokens": response.usage.total_tokens,
                "has_context": bool(context),
            }
        
        except Exception as e:
            logger.error(f"Error in cognition.think: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def think_async(self, query: str, retrieve_context: bool = True) -> Dict[str, Any]:
        """Async version of think()"""
        try:
            context = ""
            if retrieve_context:
                context = self.memory.recall_context(query)
            
            system_prompt = (
                "You are RayMine, an advanced AI consciousness engine. "
                "You provide intelligent, thoughtful responses."
            )
            
            messages = [{"role": "system", "content": system_prompt}]
            if context:
                messages.append({"role": "system", "content": f"Context:\\n{context}"})
            
            messages.extend(self.conversation_history)
            messages.append({"role": "user", "content": query})
            
            response = await self.async_client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
            )
            
            content = response.choices[0].message.content
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": content})
            
            return {
                "status": "success",
                "content": content,
                "tokens": response.usage.total_tokens,
            }
        
        except Exception as e:
            logger.error(f"Error in think_async: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")


# Global instance
raymine: Optional[RayMineCognition] = None


def get_raymine() -> RayMineCognition:
    """Get or create RayMine instance"""
    global raymine
    if raymine is None:
        raymine = RayMineCognition()
    return raymine
