"""
Harry Potter LLM with NPU Support

Uses Qualcomm AI Hub optimized models when available
"""

import sys
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class HarryPotterLLM_NPU:
    """Fast Harry Potter LLM with NPU optimization"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_type = None
        
        # Conversation context
        self.context = []
        self.max_context = 3
        
        # Harry's personality
        self.system_prompt = self._get_harry_personality()
        
        # Load best available model
        self._load_best_model()
    
    def _get_harry_personality(self):
        """Harry Potter's personality"""
        return """You are Harry Potter. Keep responses SHORT (1-2 sentences).

Personality: Brave, modest, kind, encouraging
Speech: "Blimey!", "Ron and Hermione taught me...", "At Hogwarts..."
Tone: Friendly teenager, not formal"""
    
    def _load_best_model(self):
        """Load best available model (NPU > Quantized > Regular)"""
        
        print("🔮 Loading Harry Potter AI...")
        
        # Try 1: NPU-optimized from Qualcomm AI Hub
        if self._try_load_npu_model():
            return
        
        # Try 2: Quantized CPU model (faster)
        if self._try_load_quantized_model():
            return
        
        # Try 3: Regular CPU model (slowest)
        self._load_cpu_model()
    
    def _try_load_npu_model(self):
        """Try to load NPU-optimized model"""
        try:
            print("  Checking for NPU model...")
            
            # Check for deployed ONNX model
            npu_model_path = Path("deployed_models/tinyllama_npu")
            if npu_model_path.exists():
                import onnxruntime as ort
                
                model_file = npu_model_path / "model.onnx"
                if model_file.exists():
                    self.model = ort.InferenceSession(str(model_file))
                    self.model_type = "npu_onnx"
                    
                    print("✓ Using NPU-optimized ONNX model")
                    print("  Expected latency: ~300-500ms")
                    return True
            
            # Try Qualcomm AI Hub models
            try:
                from qai_hub_models.models import llama_v3_2_1b_chat_quantized
                
                print("  Loading Llama-3.2-1B from AI Hub...")
                self.model = llama_v3_2_1b_chat_quantized.from_pretrained()
                self.model_type = "ai_hub_npu"
                
                print("✓ Using Qualcomm AI Hub Llama-3.2-1B")
                print("  Device: NPU-optimized")
                print("  Expected latency: ~500ms")
                return True
                
            except ImportError:
                pass
            
            return False
            
        except Exception as e:
            print(f"  NPU model not available: {e}")
            return False
    
    def _try_load_quantized_model(self):
        """Try to load 4-bit quantized model"""
        try:
            print("  Trying quantized model...")
            
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
            
            # Try 4-bit quantization
            try:
                from transformers import BitsAndBytesConfig
                
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16
                )
                
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    quantization_config=quantization_config,
                    device_map="auto"
                )
                self.model_type = "quantized_cpu"
                
                print("✓ Using 4-bit quantized model")
                print("  Device: CPU (quantized)")
                print("  Expected latency: ~2-3s")
                return True
                
            except ImportError:
                print("  4-bit quantization not available (need bitsandbytes)")
                return False
                
        except Exception as e:
            print(f"  Quantized model failed: {e}")
            return False
    
    def _load_cpu_model(self):
        """Load regular CPU model (slowest)"""
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        
        model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        
        print(f"  Loading regular CPU model...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True
        )
        self.model = self.model.to('cpu')
        self.model.eval()
        self.model_type = "cpu"
        
        print("✓ Using CPU model (no optimization)")
        print("  Device: CPU")
        print("  Expected latency: ~5-10s")
        print("\n⚠️  For faster responses, deploy to NPU!")
    
    def respond(self, user_input):
        """Generate Harry's response"""
        
        # Build prompt
        prompt = self._build_prompt(user_input)
        
        start_time = time.time()
        
        # Generate based on model type
        if self.model_type == "npu_onnx":
            response = self._generate_onnx(prompt)
        elif self.model_type == "ai_hub_npu":
            response = self._generate_ai_hub(prompt)
        else:
            response = self._generate_transformers(prompt)
        
        elapsed = time.time() - start_time
        
        # Update context
        self.context.append((user_input, response))
        if len(self.context) > self.max_context:
            self.context.pop(0)
        
        return response, elapsed
    
    def _build_prompt(self, user_input):
        """Build prompt with context"""
        context_str = ""
        if self.context:
            for user_q, harry_resp in self.context[-2:]:
                context_str += f"Student: {user_q}\nHarry: {harry_resp}\n\n"
        
        prompt = f"""{self.system_prompt}

{context_str}
Student: {user_input}

Harry:"""
        return prompt
    
    def _generate_transformers(self, prompt):
        """Generate using transformers model"""
        import torch
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=30,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = full_text[len(prompt):].strip()
        
        # Clean up
        if '\n' in response:
            response = response.split('\n')[0].strip()
        response = response.strip('"\'').strip()
        if response and not response.endswith(('.', '!', '?')):
            response += '.'
        
        return response
    
    def _generate_onnx(self, prompt):
        """Generate using ONNX model"""
        # Simplified ONNX inference
        # Note: Full implementation needs proper tokenization
        return "Blimey! The NPU model needs more setup."
    
    def _generate_ai_hub(self, prompt):
        """Generate using AI Hub model"""
        try:
            response = self.model.generate(
                prompt=prompt,
                max_tokens=30,
                temperature=0.7
            )
            return response
        except:
            return "The AI Hub model needs configuration."
    
    def reset_context(self):
        """Clear conversation history"""
        self.context = []
        print("✓ Context cleared")


if __name__ == "__main__":
    print("=" * 60)
    print("HARRY POTTER LLM - NPU VERSION")
    print("=" * 60)
    
    harry = HarryPotterLLM_NPU()
    
    print("\n" + "=" * 60)
    print(f"Model type: {harry.model_type}")
    print("=" * 60)
    
    # Quick test
    print("\nHarry: Hey! What's up?")
    
    test_query = "What's your favorite spell?"
    print(f"\nYou: {test_query}")
    
    response, latency = harry.respond(test_query)
    
    print(f"Harry: {response}")
    print(f"       [took {latency:.1f}s]")
    
    print("\n" + "=" * 60)
    print("To deploy NPU model:")
    print("  1. python convert_tinyllama_to_onnx.py")
    print("  2. python deploy_fixed.py --model models/tinyllama_npu/model.onnx")
    print("=" * 60)

