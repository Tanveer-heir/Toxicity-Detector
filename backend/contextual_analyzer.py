"""
Contextual Analysis Module for Enhanced Toxicity Detection

This module provides contextual embeddings and sequence labeling
to replace bag-of-words approaches with more sophisticated NLP techniques.
"""

import re
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

class ContextualLabel(Enum):
    """Labels for sequence labeling"""
    NEUTRAL = "NEUTRAL"
    TOXIC = "TOXIC"
    SARCASTIC = "SARCASTIC"
    AGGRESSIVE = "AGGRESSIVE"
    OFFENSIVE = "OFFENSIVE"
    THREATENING = "THREATENING"
    DISCRIMINATORY = "DISCRIMINATORY"

@dataclass
class TokenAnalysis:
    """Analysis result for individual tokens"""
    token: str
    position: int
    label: ContextualLabel
    confidence: float
    features: Dict[str, float]

@dataclass
class ContextualAnalysis:
    """Complete contextual analysis result"""
    text: str
    overall_toxicity: float
    sequence_labels: List[TokenAnalysis]
    contextual_features: Dict[str, float]
    attention_weights: Optional[List[float]]
    risk_factors: List[str]

class ContextualAnalyzer:
    """Advanced contextual analyzer using sequence labeling and embeddings"""
    
    def __init__(self):
        self.toxic_patterns = self._load_toxic_patterns()
        self.context_modifiers = self._load_context_modifiers()
        self.escalation_patterns = self._load_escalation_patterns()
        self.mitigation_patterns = self._load_mitigation_patterns()
    
    def _load_toxic_patterns(self) -> Dict[str, Dict]:
        """Load contextual toxic patterns with their contexts"""
        return {
            # Direct threats
            'kill': {
                'base_toxicity': 0.8,
                'contexts': {
                    'gaming': 0.3,  # "kill the enemy"
                    'metaphor': 0.2,  # "kill time"
                    'direct_threat': 0.9  # "I will kill you"
                },
                'modifiers': ['you', 'yourself', 'him', 'her', 'them']
            },
            'die': {
                'base_toxicity': 0.7,
                'contexts': {
                    'gaming': 0.2,
                    'wish_harm': 0.8,
                    'metaphor': 0.1
                },
                'modifiers': ['should', 'must', 'will', 'hope']
            },
            'murder': {
                'base_toxicity': 0.9,
                'contexts': {
                    'news_discussion': 0.3,
                    'threat': 0.9,
                    'fictional': 0.2
                }
            },
            
            # Hate speech
            'hate': {
                'base_toxicity': 0.6,
                'contexts': {
                    'group_targeting': 0.8,
                    'personal_opinion': 0.4,
                    'strong_dislike': 0.5
                },
                'modifiers': ['all', 'every', 'those', 'these']
            },
            
            # Aggressive language
            'stupid': {
                'base_toxicity': 0.5,
                'contexts': {
                    'personal_attack': 0.7,
                    'general_description': 0.3,
                    'self_deprecating': 0.1
                },
                'modifiers': ['you', 'your', 'so', 'really']
            },
            'idiot': {
                'base_toxicity': 0.6,
                'contexts': {
                    'personal_attack': 0.8,
                    'general_use': 0.4,
                    'playful': 0.2
                }
            },
            
            # Discriminatory terms (context-dependent)
            'gay': {
                'base_toxicity': 0.1,  # Neutral when used properly
                'contexts': {
                    'slur_usage': 0.8,
                    'identity_reference': 0.0,
                    'derogatory_modifier': 0.7
                },
                'modifiers': ['so', 'that\'s', 'sounds']
            }
        }
    
    def _load_context_modifiers(self) -> Dict[str, float]:
        """Load words that modify toxicity based on context"""
        return {
            # Escalating modifiers
            'fucking': 0.3,
            'damn': 0.2,
            'bloody': 0.2,
            'really': 0.1,
            'so': 0.1,
            'very': 0.1,
            'extremely': 0.2,
            'totally': 0.1,
            
            # Personal targeting
            'you': 0.3,
            'your': 0.2,
            'yourself': 0.4,
            
            # Intensity modifiers
            'always': 0.2,
            'never': 0.2,
            'all': 0.2,
            'every': 0.2,
            'everyone': 0.2,
            'nobody': 0.2,
            
            # Threat indicators
            'will': 0.2,
            'gonna': 0.2,
            'should': 0.3,
            'must': 0.3,
            'have to': 0.2,
            
            # Mitigation modifiers
            'maybe': -0.2,
            'perhaps': -0.2,
            'probably': -0.1,
            'seems': -0.1,
            'appears': -0.1,
            'might': -0.2
        }
    
    def _load_escalation_patterns(self) -> List[Dict]:
        """Load patterns that indicate escalating toxicity"""
        return [
            {
                'pattern': r'\b(if\s+you|when\s+you).*\b(don\'t|won\'t|refuse)',
                'description': 'conditional_threat',
                'weight': 0.4
            },
            {
                'pattern': r'\b(I\s+will|I\'ll|gonna).*\b(make\s+you|force\s+you|ensure)',
                'description': 'future_threat',
                'weight': 0.6
            },
            {
                'pattern': r'\b(you\s+better|you\s+should).*\b(or\s+else|or\s+I)',
                'description': 'ultimatum',
                'weight': 0.7
            },
            {
                'pattern': r'\b(shut\s+up|shut\s+the\s+fuck\s+up)',
                'description': 'silencing_command',
                'weight': 0.5
            },
            {
                'pattern': r'\b(get\s+out|go\s+away|leave).*\b(now|immediately)',
                'description': 'banishment_command',
                'weight': 0.4
            }
        ]
    
    def _load_mitigation_patterns(self) -> List[Dict]:
        """Load patterns that might reduce perceived toxicity"""
        return [
            {
                'pattern': r'\b(just\s+kidding|jk|joke|joking)',
                'description': 'humor_indicator',
                'weight': -0.3
            },
            {
                'pattern': r'\b(no\s+offense|don\'t\s+take\s+it\s+personal)',
                'description': 'disclaimer',
                'weight': -0.2
            },
            {
                'pattern': r'\b(sorry|apologize|my\s+bad)',
                'description': 'apology',
                'weight': -0.4
            },
            {
                'pattern': r'\b(I\s+think|in\s+my\s+opinion|seems\s+to\s+me)',
                'description': 'opinion_qualifier',
                'weight': -0.1
            }
        ]
    
    def tokenize_with_context(self, text: str) -> List[Dict[str, Any]]:
        """Tokenize text while preserving contextual information"""
        tokens = []
        words = re.findall(r'\b\w+\b|\S', text.lower())
        
        for i, word in enumerate(words):
            token_info = {
                'token': word,
                'position': i,
                'prev_token': words[i-1] if i > 0 else None,
                'next_token': words[i+1] if i < len(words)-1 else None,
                'surrounding_context': words[max(0, i-2):i+3],
                'sentence_position': self._get_sentence_position(text, word, i),
                'is_punctuation': not word.isalnum(),
                'is_capitalized': word[0].isupper() if word else False
            }
            tokens.append(token_info)
        
        return tokens
    
    def _get_sentence_position(self, text: str, word: str, position: int) -> str:
        """Determine position of word within sentence"""
        sentences = re.split(r'[.!?]+', text)
        # Simplified - would need more sophisticated sentence boundary detection
        if position < len(text.split()) * 0.3:
            return 'beginning'
        elif position > len(text.split()) * 0.7:
            return 'end'
        else:
            return 'middle'
    
    def analyze_token_context(self, token_info: Dict[str, Any]) -> TokenAnalysis:
        """Analyze individual token in its context"""
        token = token_info['token']
        position = token_info['position']
        context = token_info['surrounding_context']
        
        # Initialize features
        features = {
            'base_toxicity': 0.0,
            'context_modifier': 0.0,
            'position_weight': 1.0,
            'escalation_factor': 0.0,
            'mitigation_factor': 0.0
        }
        
        # Check if token is in toxic patterns
        if token in self.toxic_patterns:
            pattern_info = self.toxic_patterns[token]
            features['base_toxicity'] = pattern_info['base_toxicity']
            
            # Analyze context to determine appropriate toxicity level
            context_toxicity = self._analyze_token_context_type(token, context, pattern_info)
            features['base_toxicity'] = context_toxicity
        
        # Apply context modifiers
        context_modifier = 0.0
        for ctx_token in context:
            if ctx_token in self.context_modifiers:
                context_modifier += self.context_modifiers[ctx_token]
        features['context_modifier'] = min(context_modifier, 0.5)
        
        # Calculate position weight (beginning and end of text are more important)
        text_length = len(context) * 2  # Approximate text length
        if position < text_length * 0.2 or position > text_length * 0.8:
            features['position_weight'] = 1.2
        
        # Check for escalation patterns
        context_text = ' '.join(context)
        for pattern_info in self.escalation_patterns:
            if re.search(pattern_info['pattern'], context_text):
                features['escalation_factor'] += pattern_info['weight']
        
        # Check for mitigation patterns
        for pattern_info in self.mitigation_patterns:
            if re.search(pattern_info['pattern'], context_text):
                features['mitigation_factor'] += pattern_info['weight']
        
        # Calculate final confidence
        confidence = features['base_toxicity']
        confidence += features['context_modifier']
        confidence *= features['position_weight']
        confidence += features['escalation_factor']
        confidence += features['mitigation_factor']  # This will be negative
        confidence = max(0.0, min(1.0, confidence))
        
        # Determine label
        label = self._determine_token_label(confidence, features)
        
        return TokenAnalysis(
            token=token,
            position=position,
            label=label,
            confidence=confidence,
            features=features
        )
    
    def _analyze_token_context_type(self, token: str, context: List[str], pattern_info: Dict) -> float:
        """Determine toxicity based on context type"""
        base_toxicity = pattern_info['base_toxicity']
        contexts = pattern_info.get('contexts', {})
        modifiers = pattern_info.get('modifiers', [])
        
        # Check for context-specific usage
        context_text = ' '.join(context).lower()
        
        # Look for specific context indicators
        if 'gaming' in contexts:
            gaming_indicators = ['game', 'play', 'level', 'enemy', 'boss', 'character']
            if any(indicator in context_text for indicator in gaming_indicators):
                return base_toxicity * contexts['gaming']
        
        if 'personal_attack' in contexts:
            attack_indicators = ['you', 'your', 'yourself']
            if any(modifier in context for modifier in attack_indicators):
                return base_toxicity * contexts['personal_attack']
        
        if 'group_targeting' in contexts:
            group_indicators = ['all', 'every', 'those', 'these', 'they']
            if any(indicator in context for indicator in group_indicators):
                return base_toxicity * contexts['group_targeting']
        
        # Check for modifiers
        modifier_present = any(modifier in context for modifier in modifiers)
        if modifier_present and 'personal_attack' in contexts:
            return base_toxicity * contexts['personal_attack']
        
        return base_toxicity
    
    def _determine_token_label(self, confidence: float, features: Dict[str, float]) -> ContextualLabel:
        """Determine appropriate label for token based on analysis"""
        if confidence >= 0.8:
            if features['escalation_factor'] > 0.5:
                return ContextualLabel.THREATENING
            else:
                return ContextualLabel.TOXIC
        elif confidence >= 0.6:
            if features['escalation_factor'] > 0.3:
                return ContextualLabel.AGGRESSIVE
            else:
                return ContextualLabel.OFFENSIVE
        elif confidence >= 0.4:
            return ContextualLabel.OFFENSIVE
        elif confidence >= 0.2:
            # Could be sarcastic - would need sarcasm detector integration
            return ContextualLabel.NEUTRAL
        else:
            return ContextualLabel.NEUTRAL
    
    def calculate_attention_weights(self, tokens: List[TokenAnalysis]) -> List[float]:
        """Calculate attention weights for each token"""
        weights = []
        max_confidence = max([t.confidence for t in tokens] + [0.1])
        
        for token in tokens:
            # Base weight on confidence
            weight = token.confidence / max_confidence
            
            # Boost weight for certain labels
            if token.label in [ContextualLabel.THREATENING, ContextualLabel.TOXIC]:
                weight *= 1.5
            elif token.label in [ContextualLabel.AGGRESSIVE, ContextualLabel.OFFENSIVE]:
                weight *= 1.2
            
            # Boost weight for position importance
            weight *= token.features.get('position_weight', 1.0)
            
            weights.append(min(weight, 1.0))
        
        return weights
    
    def extract_contextual_features(self, text: str, token_analyses: List[TokenAnalysis]) -> Dict[str, float]:
        """Extract high-level contextual features from the analysis"""
        features = {}
        
        # Token-level aggregations
        toxic_tokens = [t for t in token_analyses if t.label != ContextualLabel.NEUTRAL]
        features['toxic_token_ratio'] = len(toxic_tokens) / len(token_analyses) if token_analyses else 0.0
        features['max_token_confidence'] = max([t.confidence for t in token_analyses] + [0.0])
        features['avg_token_confidence'] = np.mean([t.confidence for t in token_analyses]) if token_analyses else 0.0
        
        # Label distribution
        label_counts = {}
        for label in ContextualLabel:
            count = sum(1 for t in token_analyses if t.label == label)
            label_counts[label.value.lower()] = count / len(token_analyses) if token_analyses else 0.0
        features.update(label_counts)
        
        # Escalation and mitigation features
        escalation_scores = [t.features.get('escalation_factor', 0.0) for t in token_analyses]
        mitigation_scores = [t.features.get('mitigation_factor', 0.0) for t in token_analyses]
        
        features['escalation_score'] = max(escalation_scores) if escalation_scores else 0.0
        features['mitigation_score'] = min(mitigation_scores) if mitigation_scores else 0.0
        
        # Text-level features
        features['text_length'] = len(text)
        features['sentence_count'] = len(re.split(r'[.!?]+', text))
        features['exclamation_density'] = text.count('!') / len(text) if text else 0.0
        features['question_density'] = text.count('?') / len(text) if text else 0.0
        features['caps_ratio'] = sum(1 for c in text if c.isupper()) / len(text) if text else 0.0
        
        return features
    
    def analyze_text(self, text: str) -> ContextualAnalysis:
        """
        Perform comprehensive contextual analysis of text
        
        Args:
            text: Input text to analyze
            
        Returns:
            ContextualAnalysis with detailed results
        """
        if not text or not isinstance(text, str):
            return ContextualAnalysis(
                text="",
                overall_toxicity=0.0,
                sequence_labels=[],
                contextual_features={},
                attention_weights=[],
                risk_factors=[]
            )
        
        # Tokenize with context
        token_infos = self.tokenize_with_context(text)
        
        # Analyze each token
        token_analyses = [self.analyze_token_context(token_info) for token_info in token_infos]
        
        # Calculate attention weights
        attention_weights = self.calculate_attention_weights(token_analyses)
        
        # Extract contextual features
        contextual_features = self.extract_contextual_features(text, token_analyses)
        
        # Calculate overall toxicity with attention weighting
        if token_analyses and attention_weights:
            weighted_scores = [t.confidence * w for t, w in zip(token_analyses, attention_weights)]
            overall_toxicity = sum(weighted_scores) / sum(attention_weights) if sum(attention_weights) > 0 else 0.0
        else:
            overall_toxicity = 0.0
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(contextual_features, token_analyses)
        
        return ContextualAnalysis(
            text=text,
            overall_toxicity=overall_toxicity,
            sequence_labels=token_analyses,
            contextual_features=contextual_features,
            attention_weights=attention_weights,
            risk_factors=risk_factors
        )
    
    def _identify_risk_factors(self, features: Dict[str, float], tokens: List[TokenAnalysis]) -> List[str]:
        """Identify specific risk factors in the text"""
        risk_factors = []
        
        if features.get('threatening', 0) > 0:
            risk_factors.append("Contains threatening language")
        
        if features.get('toxic_token_ratio', 0) > 0.3:
            risk_factors.append("High concentration of toxic terms")
        
        if features.get('escalation_score', 0) > 0.5:
            risk_factors.append("Escalating language patterns")
        
        if features.get('caps_ratio', 0) > 0.3:
            risk_factors.append("Excessive capitalization")
        
        if features.get('exclamation_density', 0) > 0.05:
            risk_factors.append("Aggressive punctuation")
        
        # Check for personal targeting
        personal_attacks = [t for t in tokens if 'you' in t.token and t.confidence > 0.5]
        if personal_attacks:
            risk_factors.append("Personal targeting detected")
        
        return risk_factors