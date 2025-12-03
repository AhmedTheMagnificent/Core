import google.generativeai as genai

models = genai.list_models()

for m in models:
    print(m)