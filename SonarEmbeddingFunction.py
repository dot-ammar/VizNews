from chromadb import Documents, EmbeddingFunction, Embeddings
from sonar.inference_pipelines.text import TextToEmbeddingModelPipeline
import torch 

if torch.backends.mps.is_available():
    device = torch.device("mps")
    x = torch.ones(1, device=device)
    print (x)
else:
    print ("MPS device not found.")
    
class SonarEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        # Initialize the model once when the class is instantiated
        self.t2vec_model = TextToEmbeddingModelPipeline(
            encoder="text_sonar_basic_encoder",
            tokenizer="text_sonar_basic_encoder",
            device=device
        )
        self.max_token_length = 512
    
    def __call__(self, input: Documents) -> Embeddings:
        # Reuse the already initialized model
        embeddings = self.t2vec_model.predict(input, source_lang="eng_Latn")        
        embeddings_as_list = embeddings.tolist()
        
        return embeddings_as_list
    
    