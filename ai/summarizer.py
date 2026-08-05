import re
from collections import Counter


class TextSummarizer:
    def __init__(self):
        self.stop_words = set([
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
            'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were',
            'will', 'with', 'the', 'this', 'but', 'they', 'have', 'had', 'not', 'or',
            'we', 'you', 'your', 'their', 'them', 'his', 'her', 'she', 'i', 'me', 'my',
            'our', 'us', 'can', 'could', 'should', 'would', 'may', 'might', 'must',
            'shall', 'do', 'does', 'did', 'done', 'being', 'been', 'am', 'are', 'was'
        ])

    def summarize(self, text, max_sentences=5, min_sentences=2):
        if not text:
            return {'summary': '', 'key_points': [], 'compression_ratio': 0.0}

        sentences = self._split_sentences(text)
        if len(sentences) <= min_sentences:
            return {
                'summary': text.strip(),
                'key_points': sentences,
                'compression_ratio': 1.0
            }

        word_freq = self._calculate_word_frequencies(text)
        sentence_scores = self._score_sentences(sentences, word_freq)

        ranked_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        top_sentences = [sentences[idx] for idx, _ in ranked_sentences[:max_sentences]]
        top_sentences.sort(key=lambda s: sentences.index(s))

        summary = ' '.join(top_sentences)
        key_points = self._extract_key_points(sentences, word_freq, top_sentences)

        original_words = len(text.split())
        summary_words = len(summary.split())
        compression_ratio = round(summary_words / original_words, 2) if original_words > 0 else 0

        return {
            'summary': summary,
            'key_points': key_points,
            'compression_ratio': compression_ratio
        }

    def _split_sentences(self, text):
        text = re.sub(r'\s+', ' ', text.strip())
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _calculate_word_frequencies(self, text):
        words = re.findall(r'\b\w+\b', text.lower())
        filtered_words = [w for w in words if w not in self.stop_words and len(w) > 2]
        return Counter(filtered_words)

    def _score_sentences(self, sentences, word_freq):
        scores = {}
        for idx, sentence in enumerate(sentences):
            words = re.findall(r'\b\w+\b', sentence.lower())
            filtered = [w for w in words if w not in self.stop_words and len(w) > 2]
            if not filtered:
                scores[idx] = 0
                continue

            score = sum(word_freq.get(w, 0) for w in filtered) / len(filtered)
            if len(words) > 50:
                score *= 0.8
            scores[idx] = score

        return scores

    def _extract_key_points(self, sentences, word_freq, top_sentences):
        key_points = []
        for sentence in top_sentences[:3]:
            words = re.findall(r'\b\w+\b', sentence.lower())
            filtered = [w for w in words if w not in self.stop_words and len(w) > 2]
            if filtered:
                key_points.append(sentence)

        return key_points

    def extract_keywords(self, text, top_n=10):
        if not text:
            return []

        word_freq = self._calculate_word_frequencies(text)
        return [word for word, _ in word_freq.most_common(top_n)]

    def detect_language(self, text):
        if not text:
            return 'en'

        common_english = ['the', 'and', 'is', 'in', 'to', 'of', 'that', 'for', 'with']
        common_spanish = ['el', 'la', 'los', 'las', 'de', 'que', 'y', 'en', 'un', 'una']
        common_french = ['le', 'la', 'les', 'de', 'et', 'en', 'un', 'une', 'que', 'pour']

        words = set(text.lower().split())
        en_count = len(words.intersection(common_english))
        es_count = len(words.intersection(common_spanish))
        fr_count = len(words.intersection(common_french))

        if es_count > en_count and es_count > fr_count:
            return 'es'
        elif fr_count > en_count and fr_count > es_count:
            return 'fr'
        return 'en'

    def detect_sentiment(self, text):
        if not text:
            return 'neutral'

        positive_words = set([
            'good', 'great', 'excellent', 'positive', 'success', 'successful',
            'secure', 'safe', 'protected', 'resolved', 'recovered', 'beneficial',
            'helpful', 'improved', 'enhanced', 'strengthened', 'valid', 'verified'
        ])
        negative_words = set([
            'bad', 'poor', 'negative', 'failure', 'failed', 'breach', 'compromised',
            'attack', 'malicious', 'dangerous', 'threat', 'vulnerability', 'exploit',
            'stolen', 'leaked', 'fraud', 'scam', 'phishing', 'ransomware', 'malware',
            'suspicious', 'unauthorized', 'illegal', 'criminal', 'violation'
        ])

        words = set(text.lower().split())
        pos_count = len(words.intersection(positive_words))
        neg_count = len(words.intersection(negative_words))

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'