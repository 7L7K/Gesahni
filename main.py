"""Entry point for running the assistant."""
import yaml
from src.assistant.core import Assistant


def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as fh:
        return yaml.safe_load(fh)


def main() -> None:
    config = load_config('config.yaml')
    assistant = Assistant()
    # Normally we would pass config to components.
    print(f"Loaded config for {config.get('name')}")
    # Placeholder for processing
    result = assistant.process_audio('sample.wav')
    print(f"Processed audio: {result}")


if __name__ == '__main__':
    main()
