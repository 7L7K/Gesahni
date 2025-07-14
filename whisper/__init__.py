class DummyModel:
    def transcribe(self, path):
        return {"text": ""}

def load_model(name="base"):
    return DummyModel()
