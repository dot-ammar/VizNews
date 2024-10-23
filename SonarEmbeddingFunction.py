from chromadb import Documents, EmbeddingFunction, Embeddings
from sonar.inference_pipelines.text import TextToEmbeddingModelPipeline
import torch 

device = torch.device("mps")

class SonarEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        # Initialize the model once when the class is instantiated
        self.t2vec_model = TextToEmbeddingModelPipeline(
            encoder="text_sonar_basic_encoder",
            tokenizer="text_sonar_basic_encoder",
            device=device
        )

    def __call__(self, input: Documents) -> Embeddings:
        # Reuse the already initialized model
        embeddings = self.t2vec_model.predict(input, source_lang="eng_Latn")        
        embeddings_as_list = embeddings.tolist()
        
        return embeddings_as_list