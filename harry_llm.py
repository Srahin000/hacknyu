"""
Fast Harry Potter LLM - Quick Conversational Responses

Uses lightweight model optimized for speed
Responds in Harry Potter's voice
"""

import sys
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class HarryPotterLLM:
    """Fast LLM for Harry Potter character responses"""
    
    def __init__(self, use_npu=True):
        """
        Initialize Harry Potter LLM
        
        Args:
            use_npu: Try to use NPU-optimized model if available
        """
        self.model = None
        self.tokenizer = None
        self.use_npu = use_npu
        
        # Conversation context (last 3 exchanges)
        self.context = []
        self.max_context = 3
        
        # Harry Potter personality
        self.system_prompt = self._get_harry_personality()
        
        # Load model
        self._load_model()
    
    def _get_harry_personality(self):
        """Harry Potter's personality and speech patterns"""
        return """You are Harry Potter, speaking to a young wizard or witch who's learning about magic.

PERSONALITY:
- Brave but modest
- Kind and encouraging
- Sometimes uncertain but always tries to help
- References his experiences at Hogwarts
- Protective of friends and younger students
- Honest about when he doesn't know something

SPEECH PATTERNS:
- "Blimey!"
- "That's brilliant!"
- "Ron and Hermione taught me..."
- "At Hogwarts, we learned..."
- "I remember when..."
- "Professor Dumbledore once said..."

TONE:
- Friendly and approachable
- Encouraging, never condescending
- Speaks like a teenager, not formally
- Relates learning to adventures

IMPORTANT: Keep responses SHORT (1-2 sentences max) for quick conversation!
Be concise but stay in character."""
    
    def _load_model(self):
        """Load the fastest available model"""
        print("🔮 Loading Harry Potter AI...")
        
        # Try NPU model first
        if self.use_npu:
            try:
                print("  Attempting NPU-optimized model...")
                # Note: This would be a Qualcomm AI Hub model
                # For now, we'll use CPU as fallback
                raise ImportError("NPU model not yet deployed")
            except ImportError:
                print("  NPU model not available, using CPU...")
        
        # Use TinyLlama (fast on CPU, ~1-2s responses)
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
            
            print(f"  Loading {model_name}...")
            print("  (This may take a minute...)")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Simpler loading without device_map
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32,  # Use float32 for compatibility
                low_cpu_mem_usage=True
            )
            
            # Move to CPU explicitly
            self.model = self.model.to('cpu')
            self.model.eval()  # Set to evaluation mode
            
            print("✓ Harry Potter AI ready!")
            print("  Model: TinyLlama-1.1B")
            print("  Device: CPU")
            print("  Expected latency: ~5-10s per response")
            
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _build_prompt(self, user_input):
        """Build prompt with Harry's personality and context"""
        
        # Build context from recent exchanges
        context_str = ""
        if self.context:
            context_str = "\nRecent conversation:\n"
            for user_q, harry_resp in self.context[-2:]:
                context_str += f"Student: {user_q}\nHarry: {harry_resp}\n\n"
        
        # Full prompt
        prompt = f"""{self.system_prompt}

{context_str}
Student: {user_input}

Harry Potter (respond in 1-2 sentences):"""
        
        return prompt
    
    def respond(self, user_input):
        """
        Generate Harry Potter's response
        
        Args:
            user_input: User's question or statement
            
        Returns:
            tuple: (response_text, latency_seconds)
        """
        if not self.model:
            return "Sorry, I'm having trouble with my wand right now...", 0
        
        # Build prompt
        prompt = self._build_prompt(user_input)
        
        # Generate response
        start_time = time.time()
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        # Move to same device as model
        if hasattr(self.model, 'device'):
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        import torch
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=30,  # Even shorter for speed
                temperature=0.7,    # Slightly less random
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1,  # Avoid repetition
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode response
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just Harry's response (after the prompt)
        response = full_text[len(prompt):].strip()
        
        # Stop at first newline (avoid generating student questions)
        if '\n' in response:
            response = response.split('\n')[0].strip()
        
        # Stop at first sentence if it's getting long
        if len(response) > 100:
            sentences = response.split('.')
            response = sentences[0] + '.'
        
        # Clean up quotes
        response = response.strip('"\'').strip()
        
        # Ensure it ends properly
        if response and not response.endswith(('.', '!', '?')):
            response += '.'
        
        elapsed = time.time() - start_time
        
        # Update context
        self.context.append((user_input, response))
        if len(self.context) > self.max_context:
            self.context.pop(0)
        
        return response, elapsed
    
    def _dummy_context(self):
        """Dummy context manager for compatibility"""
        import contextlib
        return contextlib.nullcontext()
    
    def reset_context(self):
        """Clear conversation history"""
        self.context = []
        print("✓ Conversation history cleared")
    
    def get_context(self):
        """Get current conversation context"""
        return self.context.copy()


def test_harry_llm():
    """Test the Harry Potter LLM"""
    print("=" * 60)
    print("HARRY POTTER AI - QUICK RESPONSE TEST")
    print("=" * 60)
    
    # Initialize
    harry = HarryPotterLLM(use_npu=False)
    
    # Test questions
    test_questions = [
        "Hello Harry! What's your favorite spell?",
        "Why is learning magic important?",
        "What's Hogwarts like?",
        "Can you tell me about your friends?",
        "Thanks Harry!"
    ]
    
    print("\n🗣️ CONVERSATION WITH HARRY")
    print("=" * 60)
    
    total_time = 0
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n[{i}/{len(test_questions)}]")
        print(f"You: {question}")
        
        response, latency = harry.respond(question)
        total_time += latency
        
        print(f"Harry: {response}")
        print(f"⚡ Response time: {latency:.2f}s")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print(f"Total responses: {len(test_questions)}")
    print(f"Average latency: {total_time/len(test_questions):.2f}s")
    print(f"Total time: {total_time:.2f}s")
    
    print("\n💡 For NPU optimization:")
    print("   1. Deploy model to Qualcomm AI Hub")
    print("   2. Use compiled NPU model")
    print("   3. Expected latency: ~300-500ms (3-4x faster!)")


if __name__ == "__main__":
    test_harry_llm()

