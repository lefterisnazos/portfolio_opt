from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline
from transformers import DebertaTokenizer, DebertaForSequenceClassification



# Load the tokenizer and model
tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
model = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')


# Initialize sentiment-analysis pipeline
nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

result = nlp([' In August, second-quarter earnings and revenue topped analyst estimates and Best Buy raised its full-year profit guidance',
             'Best Buy CEO Corie Barry also said on the earnings call that demand spurred by artificial intelligence applications should help boost sales',
             'We believe we are just at the beginning of the impact of AI on tech innovation and customer demand,” she said',
             'The CEO fired 5% of the company to reduce costs',
             'The CEO fired 5% of the company'])

print(result)

