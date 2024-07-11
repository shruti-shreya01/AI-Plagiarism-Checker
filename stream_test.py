import streamlit as st
from transformers import GPT2Tokenizer, GPT2LMHeadModel
# from transformers.modeling_gpt2 import GPT2LMHeadModel
# from transformers.tokenization_gpt2 import GPT2Tokenizer
import torch
import nltk
from nltk.util import ngrams
from nltk.lm.preprocessing import pad_sequence
from nltk.probability import FreqDist
import plotly.express as px
from collections import Counter
from nltk.corpus import stopwords
import string



nltk.download('punkt')
nltk.download('stopwords')

# Load GPT-2 tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')

def calculate_perplexity(text):
    encoded_input = tokenizer.encode(text, add_special_tokens=False, return_tensors='pt')
    input_ids = encoded_input[0]

    with torch.no_grad():
        outputs = model(input_ids)
        logits = outputs.logits

    perplexity = torch.exp(torch.nn.functional.cross_entropy(logits.view(-1, logits.size(-1)), input_ids.view(-1)))
    return perplexity.item()

def calculate_burstiness(text):
    tokens = nltk.word_tokenize(text.lower())
    word_freq = FreqDist(tokens)
    repeated_count = sum(count > 1 for count in word_freq.values())
    burstiness_score = repeated_count / len(word_freq)
    return burstiness_score

def highlight_ai_generated(text, threshold_perplexity=30000, threshold_burstiness=0.2):
    segments = []
    tokenized_text = nltk.sent_tokenize(text)
    
    for segment in tokenized_text:
        perplexity = calculate_perplexity(segment)
        burstiness_score = calculate_burstiness(segment)
        
        if perplexity > threshold_perplexity and burstiness_score < threshold_burstiness:
            segments.append((segment, "AI Generated"))
        else:
            segments.append((segment, "Human Generated"))
    
    return segments

st.set_page_config(layout="wide")

st.title("AI DupliGuard")
text_area = st.text_area("Enter text", "")

if text_area is not None:
    if st.button("Analyze"):
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.info("Your Input Text")
            st.success(text_area)
        
        with col2:
            st.info("Detection Score")
            perplexity = calculate_perplexity(text_area)
            burstiness_score = calculate_burstiness(text_area)

            st.write("Perplexity:", perplexity)
            st.write("Burstiness Score:", burstiness_score)

            if perplexity > 30000 and burstiness_score < 0.2:
                st.error("Text Analysis Result: AI generated content")
            else:
                st.success("Text Analysis Result: Likely not generated by AI")
            
            st.warning("Disclaimer: AI plagiarism detector apps can assist in identifying potential instances of plagiarism; however, it is important to note that their results may not be entirely flawless or completely reliable. These tools employ advanced algorithms, but they can still produce false positives or false negatives. Therefore, it is recommended to use AI plagiarism detectors as a supplementary tool alongside human judgment and manual verification for accurate and comprehensive plagiarism detection.")
        
        # Check if there are AI-generated segments to display
        segments = highlight_ai_generated(text_area)
        ai_generated_segments = [segment for segment, category in segments if category == "AI Generated"]
        
        if ai_generated_segments:
            with col3:
                st.info("AI-Generated Segments")
                for segment in ai_generated_segments:
                    st.error(segment)
        else:
            st.warning("No AI-generated segments detected.")
