from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "Helsinki-NLP/opus-mt-en-hi"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


def translate_to_hindi(text):

    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    outputs = model.generate(**inputs)

    hindi_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return hindi_text