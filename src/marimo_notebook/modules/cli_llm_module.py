"""
CLI-based LLM module for Claude Code and Gemini CLI integration
"""
import subprocess
import json
from typing import Optional, Dict, Any
import os

class CLIModel:
    """Base class for CLI-based language models"""
    
    def __init__(self, name: str, command: list[str]):
        self.name = name
        self.command = command
        self.model_id = name
    
    def prompt(self, prompt_text: str, temperature: Optional[float] = None) -> Dict[str, Any]:
        """Send a prompt to the model and return the response"""
        raise NotImplementedError

class GeminiCLI(CLIModel):
    """Gemini CLI integration"""
    
    def __init__(self, model: Optional[str] = None):
        super().__init__(
            name=f"gemini-cli{f'-{model}' if model else ''}",
            command=["gemini"]
        )
        self.model = model
    
    def prompt(self, prompt_text: str, temperature: Optional[float] = None, stream: bool = False) -> 'GeminiResponse':
        """Send a prompt to Gemini CLI"""
        cmd = self.command + ["-p", prompt_text]
        if self.model:
            cmd.extend(["-m", self.model])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse output - Gemini CLI returns plain text
            # Skip the "Loaded cached credentials." line if present
            output_lines = result.stdout.strip().split('\n')
            response_text = '\n'.join(
                line for line in output_lines 
                if not line.startswith('Loaded cached credentials')
            ).strip()
            
            return GeminiResponse(response_text)
            
        except subprocess.TimeoutExpired:
            return GeminiResponse("Error: Request timed out")
        except Exception as e:
            return GeminiResponse(f"Error: {str(e)}")

class GeminiResponse:
    """Wrapper for Gemini CLI responses to match LLM library interface"""
    
    def __init__(self, text: str):
        self._text = text
    
    def text(self) -> str:
        return self._text

class ClaudeCode(CLIModel):
    """Claude Code integration (simulated - actual calls would go through Claude Code API)"""
    
    def __init__(self):
        super().__init__(
            name="claude-code",
            command=[]  # Claude Code doesn't use CLI commands
        )
    
    def prompt(self, prompt_text: str, temperature: Optional[float] = None, stream: bool = False) -> 'ClaudeResponse':
        """
        Send a prompt to Claude Code.
        In practice, this would integrate with Claude Code's API.
        For now, this returns a placeholder that indicates Claude Code should be used directly.
        """
        return ClaudeResponse(
            "Note: Claude Code (this assistant) should be used directly through the interface. "
            "To integrate Claude into the prompt library, consider using the Anthropic API with an API key."
        )

class ClaudeResponse:
    """Wrapper for Claude responses"""
    
    def __init__(self, text: str):
        self._text = text
    
    def text(self) -> str:
        return self._text

def build_cli_models():
    """Build CLI-based models for Gemini and Claude Code"""
    gemini_cli = GeminiCLI()
    gemini_flash = GeminiCLI(model="gemini-1.5-flash-latest")
    gemini_pro = GeminiCLI(model="gemini-1.5-pro-latest")
    claude_code = ClaudeCode()
    
    return {
        "gemini-cli": gemini_cli,
        "gemini-flash-cli": gemini_flash,
        "gemini-pro-cli": gemini_pro,
        "claude-code": claude_code,
    }

def prompt_with_cli(model: CLIModel, prompt_text: str, temperature: Optional[float] = None):
    """Helper function to match the existing llm_module interface"""
    response = model.prompt(prompt_text, temperature)
    return response.text()