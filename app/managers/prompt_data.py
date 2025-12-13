import os
import json

from core.logger import Logger


class PromptManager:
    _prompt_cache = {}
    _is_initialized = False
    
    @classmethod
    def _init_manager(cls, prompts_folder="prompts", config_name="config.json"):
        if cls._is_initialized:
            return

        base_dir = os.path.dirname(os.path.dirname(__file__))
        prompt_dir = os.path.join(base_dir, prompts_folder)
        config_path = os.path.join(base_dir, config_name)

        prompt_map = cls._load_prompt_config(config_path)
        cls._prompt_cache = cls._load_all_prompts(prompt_dir, prompt_map)
        cls._is_initialized = True

    @staticmethod
    def _load_prompt_config(config_path):
        if not os.path.exists(config_path):
             return {}
        with open(config_path, "r") as f:
            config = json.load(f)
        return config.get("prompts", {})

    @staticmethod
    def _load_all_prompts(prompt_dir, prompt_map):
        prompt_cache = {}
        for name, rel_path in prompt_map.items():
            full_path = os.path.join(prompt_dir, rel_path)
            if os.path.exists(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    prompt_cache[name] = f.read()
            else:
                Logger.warning(f"Prompt file not found: {full_path}")
                pass

        return prompt_cache

    @classmethod
    def get_prompt(cls, name) -> str:
        if not cls._is_initialized:
            cls._init_manager()
            
        if name not in cls._prompt_cache:
            raise ValueError(f"Prompt '{name}' not found in loaded cache.")
        return cls._prompt_cache[name]
