from fastapi import FastAPI
from pydantic import BaseModel
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel, GPT2Tokenizer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()



origins = ["*"]

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class InputData(BaseModel):
    text: str  # Input text from the JSON request body

def load_model(model_path):
    model = GPT2LMHeadModel.from_pretrained(model_path)
    return model

def load_tokenizer(tokenizer_path):
    tokenizer = GPT2Tokenizer.from_pretrained(tokenizer_path)
    return tokenizer

@app.post("/generate_text") 
async def generate_text(input_data: InputData):
    # Use input_data.text instead of InputData.text
    print("hi")
    print(input_data.text)
    
    # Specify the correct local model path
    model_path = "custom.docx"
    
    model = load_model(model_path)
    tokenizer = load_tokenizer(model_path)
    
    ids = tokenizer.encode(input_data.text, return_tensors='pt')  # Use input_data.text
    final_outputs = model.generate(
        ids,
        do_sample=True,
        max_length=75,
        pad_token_id=model.config.eos_token_id,
        top_k=50,
        top_p=0.95,
    )
    generated_text = tokenizer.decode(final_outputs[0], skip_special_tokens=True)
    print(generated_text)  # Use print(generated_text)
    return {"generated_text": generated_text}
