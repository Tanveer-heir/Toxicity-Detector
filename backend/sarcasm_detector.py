"""
Sarcasm and Irony Detection Module

This module provides specialized detection for sarcasm and irony using
pattern matching, linguistic features, and contextual analysis.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class SarcasmIndicators:
    """Container for sarcasm detection results"""
    is_sarcastic: bool
    confidence: float
    indicators: List[str]
    score_breakdown: Dict[str, float]

class SarcasmDetector:
    """Advanced sarcasm and irony detection using linguistic patterns"""
    
    def __init__(self):
        self.sarcasm_markers = self._load_sarcasm_markers()
        self.irony_patterns = self._load_irony_patterns()
        self.contradiction_words = self._load_contradiction_words()
        self.exaggeration_patterns = self._load_exaggeration_patterns()
    
    def _load_sarcasm_markers(self) -> Dict[str, float]:
        """Load sarcasm markers with their weights"""
        return {
            # Direct sarcasm indicators
            'oh really': 0.8,
            'how wonderful': 0.7,
            'great job': 0.6,
            'well done': 0.6,
            'brilliant': 0.5,
            'fantastic': 0.5,
            'amazing': 0.4,
            'perfect': 0.4,
            'lovely': 0.4,
            'charming': 0.4,
            'delightful': 0.4,
            'marvelous': 0.4,
            'superb': 0.4,
            'outstanding': 0.4,
            'excellent': 0.3,
            
            # Sarcastic phrases
            'sure thing': 0.6,
            'yeah right': 0.9,
            'of course': 0.5,
            'obviously': 0.5,
            'clearly': 0.4,
            'naturally': 0.4,
            'certainly': 0.4,
            'absolutely': 0.3,
            
            # Dismissive markers
            'whatever': 0.7,
            'fine': 0.4,
            'okay': 0.3,
            'sure': 0.3,
            'right': 0.3,
            
            # Exaggerated expressions
            'so funny': 0.6,
            'hilarious': 0.5,
            'real funny': 0.8,
            'very funny': 0.6,
            'how original': 0.8,
            'real original': 0.8,
            'so original': 0.7,
            'very original': 0.6,
            'how clever': 0.7,
            'real clever': 0.8,
            'so clever': 0.7,
            'very clever': 0.6,
        }
    
    def _load_irony_patterns(self) -> List[Dict]:
        """Load irony detection patterns"""
        return [
            {
                'pattern': r'\b(love|enjoy|adore)\b.*\b(hate|despise|awful|terrible)\b',
                'weight': 0.7,
                'description': 'contradiction_love_hate'
            },
            {
                'pattern': r'\b(perfect|great|wonderful)\b.*\b(disaster|mess|failure|terrible)\b',
                'weight': 0.8,
                'description': 'positive_negative_contradiction'
            },
            {
                'pattern': r'\b(thanks|thank you)\b.*\b(nothing|ruin|destroy|mess up)\b',
                'weight': 0.7,
                'description': 'sarcastic_thanks'
            },
            {
                'pattern': r'\b(exactly|precisely)\b.*\b(what|how)\s+(I|we)\s+(need|want)\b.*\b(not|never)\b',
                'weight': 0.8,
                'description': 'ironic_exactness'
            },
            {
                'pattern': r'\b(just|exactly)\s+what\s+(I|we)\s+(needed|wanted)\b',
                'weight': 0.6,
                'description': 'ironic_need'
            }
        ]
    
    def _load_contradiction_words(self) -> Dict[str, List[str]]:
        """Load contradictory word pairs"""
        return {
            'positive': ['good', 'great', 'excellent', 'wonderful', 'amazing', 'fantastic', 
                        'perfect', 'beautiful', 'lovely', 'brilliant', 'superb', 'outstanding'],
            'negative': ['bad', 'terrible', 'awful', 'horrible', 'disgusting', 'pathetic',
                        'useless', 'worthless', 'stupid', 'idiotic', 'moronic', 'ridiculous'],
            'love': ['love', 'adore', 'enjoy', 'like', 'appreciate'],
            'hate': ['hate', 'despise', 'loathe', 'detest', 'can\'t stand']
        }
    
    def _load_exaggeration_patterns(self) -> List[Dict]:
        """Load patterns that indicate exaggeration (potential sarcasm)"""
        return [
            {
                'pattern': r'\b(so|very|extremely|incredibly|absolutely|totally|completely)\s+(perfect|great|wonderful|amazing)\b',
                'weight': 0.6,
                'description': 'exaggerated_positive'
            },
            {
                'pattern': r'\b(real|really|very)\s+(funny|clever|smart|brilliant)\b',
                'weight': 0.7,
                'description': 'exaggerated_compliment'
            },
            {
                'pattern': r'\b(oh\s+)?(wow|gee|golly)\b',
                'weight': 0.5,
                'description': 'sarcastic_exclamation'
            }
        ]
    
    def detect_punctuation_sarcasm(self, text: str) -> float:
        """Detect sarcasm through punctuation patterns"""
        score = 0.0
        
        # Multiple exclamation marks
        exclamation_count = len(re.findall(r'!{2,}', text))
        score += min(exclamation_count * 0.2, 0.6)
        
        # Multiple question marks
        question_count = len(re.findall(r'\?{2,}', text))
        score += min(question_count * 0.3, 0.7)
        
        # Excessive ellipsis
        ellipsis_count = len(re.findall(r'\.{3,}', text))
        score += min(ellipsis_count * 0.2, 0.4)
        
        # Mixed punctuation (!?, ?!, etc.)
        mixed_punct = len(re.findall(r'[!?]{2,}', text))
        score += min(mixed_punct * 0.3, 0.6)
        
        return min(score, 1.0)
    
    def detect_capitalization_sarcasm(self, text: str) -> float:
        """Detect sarcasm through capitalization patterns"""
        score = 0.0
        words = text.split()
        
        if not words:
            return 0.0
        
        # Count words in all caps
        all_caps_words = sum(1 for word in words if len(word) > 2 and word.isupper())
        caps_ratio = all_caps_words / len(words)
        
        # Moderate caps usage might indicate sarcasm
        if 0.2 <= caps_ratio <= 0.6:
            score += caps_ratio * 0.5
        
        # Alternating caps (mocking style)
        alternating_pattern = re.search(r'\b[a-z][A-Z][a-z][A-Z]', text)
        if alternating_pattern:
            score += 0.7
        
        return min(score, 1.0)
    
    def detect_word_repetition_sarcasm(self, text: str) -> float:
        """Detect sarcasm through word repetition patterns"""
        score = 0.0
        
        # Repeated words for emphasis (e.g., "real real funny")
        repeated_words = re.findall(r'\b(\w+)\s+\1\b', text.lower())
        score += min(len(repeated_words) * 0.3, 0.6)
        
        # Repeated letters for emphasis (e.g., "sooooo funny")
        repeated_letters = re.findall(r'(\w)\1{2,}', text)
        score += min(len(repeated_letters) * 0.2, 0.4)
        
        return min(score, 1.0)
    
    def detect_contradictions(self, text: str) -> Tuple[float, List[str]]:
        """Detect contradictory statements that may indicate irony"""
        score = 0.0
        found_contradictions = []
        text_lower = text.lower()
        
        # Check for positive-negative contradictions
        pos_words = [word for word in self.contradiction_words['positive'] if word in text_lower]
        neg_words = [word for word in self.contradiction_words['negative'] if word in text_lower]
        
        if pos_words and neg_words:
            score += 0.6
            found_contradictions.append(f"positive_negative: {pos_words} vs {neg_words}")
        
        # Check for love-hate contradictions
        love_words = [word for word in self.contradiction_words['love'] if word in text_lower]
        hate_words = [word for word in self.contradiction_words['hate'] if word in text_lower]
        
        if love_words and hate_words:
            score += 0.7
            found_contradictions.append(f"love_hate: {love_words} vs {hate_words}")
        
        return min(score, 1.0), found_contradictions
    
    def detect_sarcasm_markers(self, text: str) -> Tuple[float, List[str]]:
        """Detect explicit sarcasm markers"""
        score = 0.0
        found_markers = []
        text_lower = text.lower()
        
        for marker, weight in self.sarcasm_markers.items():
            if marker in text_lower:
                score += weight
                found_markers.append(marker)
        
        return min(score, 1.0), found_markers
    
    def detect_irony_patterns(self, text: str) -> Tuple[float, List[str]]:
        """Detect irony through linguistic patterns"""
        score = 0.0
        found_patterns = []
        text_lower = text.lower()
        
        for pattern_info in self.irony_patterns:
            pattern = pattern_info['pattern']
            weight = pattern_info['weight']
            description = pattern_info['description']
            
            if re.search(pattern, text_lower):
                score += weight
                found_patterns.append(description)
        
        return min(score, 1.0), found_patterns
    
    def detect_exaggeration(self, text: str) -> Tuple[float, List[str]]:
        """Detect exaggeration patterns that may indicate sarcasm"""
        score = 0.0
        found_patterns = []
        text_lower = text.lower()
        
        for pattern_info in self.exaggeration_patterns:
            pattern = pattern_info['pattern']
            weight = pattern_info['weight']
            description = pattern_info['description']
            
            matches = re.findall(pattern, text_lower)
            if matches:
                score += weight * len(matches)
                found_patterns.extend([description] * len(matches))
        
        return min(score, 1.0), found_patterns
    
    def analyze_sarcasm(self, text: str) -> SarcasmIndicators:
        """
        Comprehensive sarcasm analysis
        
        Args:
            text: Input text to analyze
            
        Returns:
            SarcasmIndicators object with detection results
        """
        if not text or not isinstance(text, str):
            return SarcasmIndicators(False, 0.0, [], {})
        
        indicators = []
        scores = {}
        
        # Analyze different aspects
        punct_score = self.detect_punctuation_sarcasm(text)
        scores['punctuation'] = punct_score
        if punct_score > 0.3:
            indicators.append('punctuation_patterns')
        
        caps_score = self.detect_capitalization_sarcasm(text)
        scores['capitalization'] = caps_score
        if caps_score > 0.3:
            indicators.append('capitalization_patterns')
        
        repetition_score = self.detect_word_repetition_sarcasm(text)
        scores['repetition'] = repetition_score
        if repetition_score > 0.3:
            indicators.append('repetition_patterns')
        
        contradiction_score, contradictions = self.detect_contradictions(text)
        scores['contradictions'] = contradiction_score
        if contradictions:
            indicators.extend(contradictions)
        
        marker_score, markers = self.detect_sarcasm_markers(text)
        scores['sarcasm_markers'] = marker_score
        if markers:
            indicators.extend(markers)
        
        irony_score, irony_patterns = self.detect_irony_patterns(text)
        scores['irony_patterns'] = irony_score
        if irony_patterns:
            indicators.extend(irony_patterns)
        
        exaggeration_score, exag_patterns = self.detect_exaggeration(text)
        scores['exaggeration'] = exaggeration_score
        if exag_patterns:
            indicators.extend(exag_patterns)
        
        # Calculate weighted final score
        weights = {
            'sarcasm_markers': 0.3,
            'contradictions': 0.25,
            'irony_patterns': 0.2,
            'exaggeration': 0.15,
            'punctuation': 0.05,
            'capitalization': 0.03,
            'repetition': 0.02
        }
        
        final_score = sum(scores[key] * weights[key] for key in scores if key in weights)
        final_score = min(final_score, 1.0)
        
        # Determine if sarcastic based on threshold
        is_sarcastic = final_score > 0.4
        
        return SarcasmIndicators(
            is_sarcastic=is_sarcastic,
            confidence=final_score,
            indicators=indicators,
            score_breakdown=scores
        )
    
    def get_sarcasm_confidence_level(self, confidence: float) -> str:
        """Convert confidence score to human-readable level"""
        if confidence >= 0.8:
            return "Very High"
        elif confidence >= 0.6:
            return "High"
        elif confidence >= 0.4:
            return "Medium"
        elif confidence >= 0.2:
            return "Low"
        else:
            return "Very Low"