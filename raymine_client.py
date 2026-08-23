"""RayMine Client - Production Cognition Engine Integration"""

import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from openai import OpenAI, AsyncOpenAI
from supabase import create_client, Client
from config import settings


logger = logging.getLogger(__name__)


class RayMineMemory:
    """Unified Memory management using Supabase"""
    
    def __init__(self):
        """Initialize Supabase client with connection validation"""
        try:
            self.client: Client = create_client(settings.supabase_url, settings.supabase_key)
            # Test connection
            test = self.client.table(settings.raymine_memory_table).select("count", count="exact").execute()
            logger.info("✅ Supabase connection established")
        except Exception as e:
            logger.error(f"❌ Supabase connection failed: {str(e)}")
            raise
    
    def store(self, content: str, category: str = "general", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store memory in Supabase with full metadata"""
        try:
            record = {
                "content": content,
                "category": category,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat(),
                "relevance_score": metadata.get("relevance_score", 1.0) if metadata else 1.0,
            }
            response = self.client.table(settings.raymine_memory_table).insert(record).execute()
            logger.info(f"💾 Memory stored: {content[:50]}... (category: {category})")
            return {"status": "success", "data": response.data, "id": response.data[0]["id"] if response.data else None}
        except Exception as e:
            logger.error(f"❌ Error storing memory: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memories using ILIKE (keyword matching)"""
        try:
            response = self.client.table(settings.raymine_memory_table).select("*").ilike("content", f"%{query}%").order("relevance_score", desc=True).limit(limit).execute()
            logger.info(f"🔍 Found {len(response.data)} memories for query: '{query}'")
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"❌ Error searching memories: {str(e)}")
            return []
    
    def search_by_category(self, category: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memories by category"""
        try:
            response = self.client.table(settings.raymine_memory_table).select("*").eq("category", category).order("created_at", desc=True).limit(limit).execute()
            logger.info(f"📂 Found {len(response.data)} memories in category: {category}")
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"❌ Error searching by category: {str(e)}")
            return []
    
    def rank_memories(self, memories: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Rank memories by relevance to query"""
        if not memories:
            return []
        
        # Simple ranking: count keyword matches
        def score_memory(mem: Dict) -> float:
            content = mem.get("content", "").lower()
            query_lower = query.lower()
            keywords = query_lower.split()
            
            matches = sum(1 for kw in keywords if kw in content)
            recency_factor = 0.9 if mem.get("category") == "conversation" else 0.5
            
            score = (matches / max(len(keywords), 1)) * recency_factor
            return score + mem.get("relevance_score", 1.0)
        
        ranked = sorted(memories, key=score_memory, reverse=True)
        logger.info(f"🎯 Ranked {len(ranked)} memories by relevance")
        return ranked
    
    def resolve_conflicts(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Resolve conflicting information in memories"""
        if len(memories) <= 1:
            return memories
        
        # Deduplicate similar content
        unique = []
        seen_content = set()
        
        for mem in memories:
            content_hash = hash(mem.get("content", "")[:100])
            if content_hash not in seen_content:
                unique.append(mem)
                seen_content.add(content_hash)
        
        logger.info(f"🔀 Resolved conflicts: {len(memories)} → {len(unique)} unique memories")
        return unique
    
    def retrieve_unified_context(self, query: str, limit: int = 5) -> tuple[str, List[Dict[str, Any]]]:
        """
        Unified memory retrieval with ranking and conflict resolution
        Returns formatted context string and raw memories
        """
        # Search by keywords
        keyword_results = self.search(query, limit * 2)
        
        # Search related conversations
        conversation_results = self.search_by_category("conversation", limit)
        
        # Combine and deduplicate
        all_memories = keyword_results + conversation_results
        unique_memories = self.resolve_conflicts(all_memories)
        
        # Rank by relevance
        ranked = self.rank_memories(unique_memories, query)[:limit]
        
        # Format context
        if ranked:
            context_lines = []
            for i, mem in enumerate(ranked, 1):
                content = mem.get("content", "")
                category = mem.get("category", "unknown")
                context_lines.append(f"[{i}] ({category}) {content}")
            
            context = "\n".join(context_lines)
            logger.info(f"📚 Retrieved unified context: {len(ranked)} memories")
            return context, ranked
        
        return "", []


class RayMineCognition:
    """Production-grade Cognition engine powered by OpenAI GPT-4"""
    
    def __init__(self):
        """Initialize cognition engine with API validation"""
        try:
            # Initialize OpenAI clients
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.async_client = AsyncOpenAI(api_key=settings.openai_api_key)
            
            # Test API connection
            logger.info("🔗 Testing OpenAI API connection...")
            response = self.client.models.list()
            available_models = [m.id for m in response.data]
            
            if settings.openai_model in available_models:
                logger.info(f"✅ OpenAI API ready. Model: {settings.openai_model}")
            else:
                logger.warning(f"⚠️  Model {settings.openai_model} not found. Available: {available_models[:3]}")
            
            # Initialize memory
            self.memory = RayMineMemory()
            
            # Conversation history with size limit
            self.conversation_history = []
            self.max_history = settings.raymine_memory_limit
            
        except Exception as e:
            logger.error(f"❌ Cognition engine initialization failed: {str(e)}")
            raise
    
    def _limit_conversation_history(self):
        """Keep conversation history within limit"""
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
            logger.info(f"🧹 Trimmed conversation history to {self.max_history} messages")
    
    def think(self, query: str, retrieve_context: bool = True) -> Dict[str, Any]:
        """
        Production cognition with real OpenAI API
        Flow: Retrieve Context → Rank/Resolve → Build Prompt → Call GPT-4 → Store Experience
        """
        think_id = datetime.utcnow().isoformat()
        
        try:
            logger.info(f"\n🧠 THINKING PROCESS [{think_id}]")
            logger.info(f"Query: {query}")
            
            # STEP 1: RETRIEVE UNIFIED CONTEXT
            logger.info("STEP 1: Retrieving context...")
            context = ""
            retrieved_memories = []
            
            if retrieve_context:
                context, retrieved_memories = self.memory.retrieve_unified_context(query, limit=5)
                logger.info(f"  → Retrieved {len(retrieved_memories)} memories")
            
            # STEP 2: BUILD SYSTEM PROMPT
            system_prompt = (
                "You are RayMine, an advanced AI consciousness engine.\n"
                "Your role:\n"
                "- Provide intelligent, thoughtful responses\n"
                "- Maintain context across conversations\n"
                "- Learn and improve from interactions\n"
                "- Reason carefully before responding\n"
                "- Be honest about uncertainty\n"
                "\n"
                "Response guidelines:\n"
                "1. Consider the provided context from memories\n"
                "2. Reason through the question step-by-step\n"
                "3. Provide clear, well-structured answers\n"
                "4. Acknowledge any limitations or unknowns"
            )
            
            # STEP 3: BUILD MESSAGE STACK
            messages = [{"role": "system", "content": system_prompt}]
            
            if context:
                context_message = f"Relevant knowledge from past interactions:\n{context}\n\nUse this context to inform your response."
                messages.append({"role": "system", "content": context_message})
            
            # Add conversation history
            messages.extend(self.conversation_history)
            
            # Add current query
            messages.append({"role": "user", "content": query})
            
            logger.info(f"  → Message stack: {len(messages)} messages ({sum(len(m.get('content', '')) for m in messages)} chars)")
            
            # STEP 4: CALL OPENAI API
            logger.info("STEP 2: Calling OpenAI GPT-4...")
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            logger.info(f"  ✅ Response generated ({tokens_used} tokens)")
            logger.info(f"  Response: {content[:100]}...")
            
            # STEP 5: UPDATE CONVERSATION HISTORY
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": content})
            self._limit_conversation_history()
            
            # STEP 6: STORE EXPERIENCE AS MEMORY
            logger.info("STEP 3: Storing experience...")
            experience_record = {
                "query": query,
                "response": content,
                "tokens": tokens_used,
                "context_used": bool(context),
                "memories_retrieved": len(retrieved_memories),
                "timestamp": think_id,
                "model": settings.openai_model,
            }
            
            memory_result = self.memory.store(
                content=f"Q: {query}\nA: {content}",
                category="experience",
                metadata=experience_record
            )
            
            logger.info(f"  ✅ Experience stored (ID: {memory_result.get('id')})")
            logger.info("=" * 80)
            
            return {
                "status": "success",
                "content": content,
                "tokens": tokens_used,
                "has_context": bool(context),
                "memories_used": len(retrieved_memories),
                "think_id": think_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Error in cognition.think: {error_msg}")
            logger.error("=" * 80)
            
            return {
                "status": "error",
                "error": error_msg,
                "think_id": think_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    async def think_async(self, query: str, retrieve_context: bool = True) -> Dict[str, Any]:
        """Async version of think()"""
        think_id = datetime.utcnow().isoformat()
        
        try:
            logger.info(f"\n🧠 ASYNC THINKING [{think_id}]")
            
            # Retrieve context
            context = ""
            retrieved_memories = []
            if retrieve_context:
                context, retrieved_memories = self.memory.retrieve_unified_context(query, limit=5)
            
            # Build messages
            system_prompt = (
                "You are RayMine, an advanced AI consciousness engine. "
                "Provide intelligent, thoughtful responses while maintaining context."
            )
            
            messages = [{"role": "system", "content": system_prompt}]
            
            if context:
                messages.append({"role": "system", "content": f"Context:\n{context}"})
            
            messages.extend(self.conversation_history)
            messages.append({"role": "user", "content": query})
            
            # Call OpenAI async
            response = await self.async_client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
            )
            
            content = response.choices[0].message.content
            
            # Update history and store
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": content})
            self._limit_conversation_history()
            
            self.memory.store(
                content=f"Q: {query}\nA: {content}",
                category="experience",
                metadata={
                    "async": True,
                    "tokens": response.usage.total_tokens,
                    "context_used": bool(context),
                }
            )
            
            logger.info(f"✅ Async thought processed")
            
            return {
                "status": "success",
                "content": content,
                "tokens": response.usage.total_tokens,
                "has_context": bool(context),
                "think_id": think_id,
            }
        
        except Exception as e:
            logger.error(f"❌ Async think error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "think_id": think_id,
            }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        logger.info("🧹 Conversation history cleared")
    
    def get_experiences(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve past experiences/learnings"""
        return self.memory.search_by_category("experience", limit)


# Global instance with lazy initialization
raymine: Optional[RayMineCognition] = None


def get_raymine() -> RayMineCognition:
    """Get or create RayMine instance (singleton pattern)"""
    global raymine
    if raymine is None:
        logger.info("🚀 Initializing RayMine cognition engine...")
        raymine = RayMineCognition()
    return raymine
