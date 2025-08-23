from transformers.pipelines import pipeline
from transformers import AutoModelForTokenClassification, AutoTokenizer


def get_standard_ner_pipeline(model_name, tokenizer_name):
    # model = AutoModelForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
    # tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-cased")
    model = AutoModelForTokenClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    return pipeline("token-classification", model=model, tokenizer=tokenizer)