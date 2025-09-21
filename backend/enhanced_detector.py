"""
Enhanced Toxicity Detector

This module integrates all the advanced features:
- Text normalization
- Sarcasm and irony detection
- Contextual analysis with sequence labeling
- Multi-task learning approach
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import numpy as np

from text_normalizer import TextNormalizer
from sarcasm_detector import SarcasmDetector, SarcasmIndicators
from contextual_analyzer import ContextualAnalyzer, ContextualAnalysis, ContextualLabel

@dataclass
class EnhancedToxicityResult:
    """Comprehensive toxicity analysis result"""
    # Original analysis
    is_toxic: bool
    confidence: float
    toxic_labels: List[str]
    scores: Dict[str, float]
    toxic_words: List[str]
    
    # Enhanced analysis
    normalized_text: str
    normalization_applied: bool
    sarcasm_analysis: Dict[str, Any]
    contextual_analysis: Dict[str, Any]
    risk_factors: List[str]
    
    # Multi-task predictions
    is_sarcastic: bool
    sarcasm_confidence: float
    context_toxicity: float
    sequence_labels: List[Dict[str, Any]]
    
    # Meta information
    processing_notes: List[str]
    model_versions: Dict[str, str]

class EnhancedToxicityDetector:
    """Advanced multi-task toxicity detector"""
    
    def __init__(self, original_classifier=None, threshold: float = 0.7):
        self.threshold = threshold
        self.original_classifier = original_classifier
        
        # Initialize enhanced components
        self.text_normalizer = TextNormalizer()
        self.sarcasm_detector = SarcasmDetector()
        self.contextual_analyzer = ContextualAnalyzer()
        
        # Weights for combining different analysis types
        self.analysis_weights = {
            'original_bert': 0.4,      # Original BERT model
            'contextual': 0.35,        # Contextual analysis
            'sarcasm_adjusted': 0.15,  # Sarcasm-adjusted toxicity
            'normalization_boost': 0.1 # Boost from normalization revealing hidden toxicity
        }
        
        self.model_versions = {
            'text_normalizer': '1.0.0',
            'sarcasm_detector': '1.0.0', 
            'contextual_analyzer': '1.0.0',
            'enhanced_detector': '1.0.0'
        }
    
    def _analyze_with_original_model(self, text: str) -> Dict[str, Any]:
        """Analyze text with original BERT model if available"""
        if not self.original_classifier:
            return {
                'is_toxic': False,
                'confidence': 0.0,
                'toxic_labels': [],
                'scores': {},
                'available': False
            }
        
        try:
            results = self.original_classifier(text)
            toxic_labels = []
            scores = {}
            max_score = 0.0
            
            for item in results[0]:
                label = item["label"]
                score = item["score"]
                scores[label] = score
                if score >= self.threshold and label.lower() != "not toxic":
                    toxic_labels.append(label)
                    if score > max_score:
                        max_score = score
            
            return {
                'is_toxic': len(toxic_labels) > 0,
                'confidence': max_score,
                'toxic_labels': toxic_labels,
                'scores': scores,
                'available': True
            }
        except Exception as e:
            return {
                'is_toxic': False,
                'confidence': 0.0,
                'toxic_labels': [],
                'scores': {},
                'available': False,
                'error': str(e)
            }
    
    def _combine_toxicity_scores(self, 
                               original_score: float,
                               contextual_score: float, 
                               sarcasm_indicators: SarcasmIndicators,
                               normalization_revealed_toxicity: bool) -> Tuple[float, List[str]]:
        """Combine scores from different analysis methods"""
        
        scores = {}
        reasoning = []
        
        # Original BERT score
        scores['original_bert'] = original_score
        if original_score > self.threshold:
            reasoning.append(f"Original model detected toxicity (confidence: {original_score:.3f})")
        
        # Contextual analysis score
        scores['contextual'] = contextual_score
        if contextual_score > 0.5:
            reasoning.append(f"Contextual analysis detected toxicity (confidence: {contextual_score:.3f})")
        
        # Sarcasm adjustment
        sarcasm_adjustment = 0.0
        if sarcasm_indicators.is_sarcastic:
            # Sarcasm can make seemingly positive statements toxic
            if sarcasm_indicators.confidence > 0.6:
                sarcasm_adjustment = min(0.3, sarcasm_indicators.confidence * 0.5)
                reasoning.append(f"Sarcasm detected, increasing toxicity assessment (+{sarcasm_adjustment:.3f})")
        
        scores['sarcasm_adjusted'] = sarcasm_adjustment
        
        # Normalization boost
        normalization_boost = 0.0
        if normalization_revealed_toxicity:
            normalization_boost = 0.2
            reasoning.append("Text normalization revealed hidden toxic content")
        
        scores['normalization_boost'] = normalization_boost
        
        # Calculate weighted final score
        final_score = sum(scores[key] * self.analysis_weights[key] for key in scores if key in self.analysis_weights)
        final_score = min(final_score, 1.0)
        
        return final_score, reasoning
    
    def _extract_enhanced_features(self, 
                                 original_result: Dict,
                                 contextual_analysis: ContextualAnalysis,
                                 sarcasm_indicators: SarcasmIndicators,
                                 normalized_text: str,
                                 original_text: str) -> Dict[str, Any]:
        """Extract comprehensive features from all analysis types"""
        
        features = {}
        
        # Original model features
        features.update({f"bert_{k}": v for k, v in original_result.get('scores', {}).items()})
        
        # Contextual features
        features.update({f"ctx_{k}": v for k, v in contextual_analysis.contextual_features.items()})
        
        # Sarcasm features
        features.update({f"sarc_{k}": v for k, v in sarcasm_indicators.score_breakdown.items()})
        features['sarcasm_confidence'] = sarcasm_indicators.confidence
        features['is_sarcastic'] = sarcasm_indicators.is_sarcastic
        
        # Normalization features
        features['text_was_normalized'] = normalized_text != original_text
        features['text_length_change'] = len(normalized_text) - len(original_text)
        features['normalization_ratio'] = len(normalized_text) / len(original_text) if original_text else 1.0
        
        return features
    
    def analyze_toxicity_enhanced(self, text: str, custom_toxic_words: set = None) -> EnhancedToxicityResult:
        """
        Perform comprehensive enhanced toxicity analysis
        
        Args:
            text: Input text to analyze
            custom_toxic_words: Optional set of custom toxic words
            
        Returns:
            EnhancedToxicityResult with comprehensive analysis
        """
        if not text or not isinstance(text, str):
            return EnhancedToxicityResult(
                is_toxic=False,
                confidence=0.0,
                toxic_labels=[],
                scores={},
                toxic_words=[],
                normalized_text="",
                normalization_applied=False,
                sarcasm_analysis={},
                contextual_analysis={},
                risk_factors=[],
                is_sarcastic=False,
                sarcasm_confidence=0.0,
                context_toxicity=0.0,
                sequence_labels=[],
                processing_notes=["Empty or invalid input"],
                model_versions=self.model_versions
            )
        
        processing_notes = []
        original_text = text
        
        # Step 1: Text Normalization
        processing_notes.append("Starting text normalization")
        normalized_text = self.text_normalizer.normalize_text(text)
        normalization_applied = normalized_text != original_text
        
        if normalization_applied:
            processing_notes.append(f"Text normalized: '{original_text[:50]}...' -> '{normalized_text[:50]}...'")
        
        # Step 2: Sarcasm Detection (on original text to preserve tone indicators)
        processing_notes.append("Analyzing sarcasm and irony")
        sarcasm_indicators = self.sarcasm_detector.analyze_sarcasm(original_text)
        
        # Step 3: Contextual Analysis (on normalized text for better understanding)
        processing_notes.append("Performing contextual analysis")
        contextual_analysis = self.contextual_analyzer.analyze_text(normalized_text)
        
        # Step 4: Original model analysis (both original and normalized)
        processing_notes.append("Running original BERT analysis")
        original_result_raw = self._analyze_with_original_model(original_text)
        original_result_normalized = self._analyze_with_original_model(normalized_text)
        
        # Check if normalization revealed hidden toxicity
        normalization_revealed_toxicity = (
            original_result_normalized.get('confidence', 0) > original_result_raw.get('confidence', 0) + 0.1
        )
        
        if normalization_revealed_toxicity:
            processing_notes.append("Normalization revealed additional toxic content")
        
        # Step 5: Find custom toxic words (on both original and normalized)
        toxic_words = []
        if custom_toxic_words:
            # This would integrate with the existing find_custom_toxic_words function
            # For now, simplified implementation
            text_lower = normalized_text.lower()
            for word in custom_toxic_words:
                if word.lower() in text_lower:
                    toxic_words.append(word)
        
        # Step 6: Combine all analyses
        processing_notes.append("Combining multi-task analysis results")
        
        # Use the better of original or normalized BERT results
        best_original_result = original_result_normalized if normalization_revealed_toxicity else original_result_raw
        
        final_confidence, reasoning = self._combine_toxicity_scores(
            original_score=best_original_result.get('confidence', 0.0),
            contextual_score=contextual_analysis.overall_toxicity,
            sarcasm_indicators=sarcasm_indicators,
            normalization_revealed_toxicity=normalization_revealed_toxicity
        )
        
        processing_notes.extend(reasoning)
        
        # Determine final toxicity
        is_toxic = (
            final_confidence > self.threshold or
            len(toxic_words) > 0 or
            any(label != ContextualLabel.NEUTRAL for token in contextual_analysis.sequence_labels for label in [token.label])
        )
        
        # Compile toxic labels from all sources
        all_toxic_labels = []
        all_toxic_labels.extend(best_original_result.get('toxic_labels', []))
        
        # Add contextual labels
        contextual_toxic_labels = list(set([
            token.label.value for token in contextual_analysis.sequence_labels 
            if token.label != ContextualLabel.NEUTRAL
        ]))
        all_toxic_labels.extend(contextual_toxic_labels)
        
        # Add sarcasm if detected as toxic sarcasm
        if sarcasm_indicators.is_sarcastic and sarcasm_indicators.confidence > 0.6:
            all_toxic_labels.append("SARCASTIC")
        
        # Remove duplicates while preserving order
        unique_toxic_labels = []
        for label in all_toxic_labels:
            if label not in unique_toxic_labels:
                unique_toxic_labels.append(label)
        
        # Compile all scores
        all_scores = {}
        all_scores.update(best_original_result.get('scores', {}))
        all_scores['contextual_toxicity'] = contextual_analysis.overall_toxicity
        all_scores['sarcasm_confidence'] = sarcasm_indicators.confidence
        all_scores['final_combined'] = final_confidence
        
        # Compile risk factors
        risk_factors = []
        risk_factors.extend(contextual_analysis.risk_factors)
        if sarcasm_indicators.is_sarcastic:
            risk_factors.append(f"Sarcasm detected (confidence: {sarcasm_indicators.confidence:.3f})")
        if normalization_revealed_toxicity:
            risk_factors.append("Hidden toxic content revealed through normalization")
        
        # Convert sequence labels to serializable format
        sequence_labels = [
            {
                'token': token.token,
                'position': token.position,
                'label': token.label.value,
                'confidence': token.confidence,
                'features': token.features
            }
            for token in contextual_analysis.sequence_labels
        ]
        
        return EnhancedToxicityResult(
            # Original format compatibility
            is_toxic=is_toxic,
            confidence=final_confidence,
            toxic_labels=unique_toxic_labels,
            scores=all_scores,
            toxic_words=toxic_words,
            
            # Enhanced features
            normalized_text=normalized_text,
            normalization_applied=normalization_applied,
            sarcasm_analysis=asdict(sarcasm_indicators),
            contextual_analysis={
                'overall_toxicity': contextual_analysis.overall_toxicity,
                'contextual_features': contextual_analysis.contextual_features,
                'attention_weights': contextual_analysis.attention_weights,
                'risk_factors': contextual_analysis.risk_factors
            },
            risk_factors=risk_factors,
            
            # Multi-task results
            is_sarcastic=sarcasm_indicators.is_sarcastic,
            sarcasm_confidence=sarcasm_indicators.confidence,
            context_toxicity=contextual_analysis.overall_toxicity,
            sequence_labels=sequence_labels,
            
            # Meta information
            processing_notes=processing_notes,
            model_versions=self.model_versions
        )
    
    def get_analysis_summary(self, result: EnhancedToxicityResult) -> Dict[str, Any]:
        """Generate a human-readable summary of the analysis"""
        summary = {
            'overall_assessment': 'TOXIC' if result.is_toxic else 'NON-TOXIC',
            'confidence': f"{result.confidence:.3f}",
            'primary_concerns': result.toxic_labels[:3] if result.toxic_labels else ['None'],
            'risk_level': self._assess_risk_level(result.confidence),
            'sarcasm_detected': result.is_sarcastic,
            'text_was_normalized': result.normalization_applied,
            'key_risk_factors': result.risk_factors[:3] if result.risk_factors else ['None'],
            'recommended_action': self._recommend_action(result)
        }
        
        return summary
    
    def _assess_risk_level(self, confidence: float) -> str:
        """Assess risk level based on confidence score"""
        if confidence >= 0.8:
            return "HIGH"
        elif confidence >= 0.6:
            return "MEDIUM-HIGH"
        elif confidence >= 0.4:
            return "MEDIUM"
        elif confidence >= 0.2:
            return "LOW-MEDIUM"
        else:
            return "LOW"
    
    def _recommend_action(self, result: EnhancedToxicityResult) -> str:
        """Recommend action based on analysis results"""
        if result.confidence >= 0.8:
            return "BLOCK_CONTENT"
        elif result.confidence >= 0.6:
            return "WARN_USER"
        elif result.confidence >= 0.4:
            return "SUGGEST_REVISION"
        elif result.is_sarcastic and result.sarcasm_confidence > 0.7:
            return "FLAG_FOR_REVIEW"
        else:
            return "ALLOW"