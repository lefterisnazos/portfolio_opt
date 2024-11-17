from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sentences = [' In August, second-quarter earnings and revenue topped analyst estimates and Best Buy raised its full-year profit guidance',
             'Best Buy CEO Corie Barry also said on the earnings call that demand spurred by artificial intelligence applications should help boost sales',
             'We believe we are just at the beginning of the impact of AI on tech innovation and customer demand,” she said',
             'The CEO fired 5% of the company to improve margins for the upcoming quarters.']

analyzer = SentimentIntensityAnalyzer()
for sentence in sentences:
    vs = analyzer.polarity_scores(sentence)
    print(f"str({vs})")
