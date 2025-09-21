# Enhanced Toxicity Detection Features

This document describes the advanced features implemented to handle sarcasm/irony detection, text normalization, and contextual analysis with sequence labeling.

## Overview

The enhanced toxicity detection system addresses the requirements specified in the problem statement:

1. **Handle sarcasm and irony detection with specialized models or multi-task learning**
2. **Normalize slang, emojis, spelling errors, and abbreviations**  
3. **Use contextual embeddings and sequence labeling instead of bag-of-words**

## New Components

### 1. Text Normalization (`text_normalizer.py`)

Comprehensive text preprocessing that converts informal text to normalized form:

#### Features:
- **Emoji normalization**: Converts emojis to text descriptions (😡 → "angry face")
- **Slang expansion**: Expands internet slang (lol → "laugh out loud")
- **Abbreviation expansion**: Expands common abbreviations (ur → "your")
- **Spelling correction**: Fixes common misspellings (recieve → "receive")
- **Case normalization**: Handles excessive capitalization
- **Character normalization**: Removes repeated characters (sooooo → "soo")

#### Usage:
```python
from text_normalizer import TextNormalizer

normalizer = TextNormalizer()
normalized = normalizer.normalize_text("OMG ur sooooo stupid 😡 lol jk")
# Result: "oh my god your soo stupid angry face laugh out loud jk"
```

### 2. Sarcasm and Irony Detection (`sarcasm_detector.py`)

Specialized detection for sarcastic and ironic content using linguistic patterns:

#### Features:
- **Pattern-based detection**: Recognizes sarcastic phrases and contradictions
- **Punctuation analysis**: Detects sarcastic punctuation patterns (!!!, ???)
- **Capitalization analysis**: Identifies mocking capitalization patterns
- **Contradiction detection**: Finds contradictory statements indicating irony
- **Exaggeration detection**: Recognizes exaggerated expressions

#### Usage:
```python
from sarcasm_detector import SarcasmDetector

detector = SarcasmDetector()
result = detector.analyze_sarcasm("Great job... really amazing work 🙄")
print(f"Sarcastic: {result.is_sarcastic}, Confidence: {result.confidence}")
```

### 3. Contextual Analysis (`contextual_analyzer.py`)

Advanced contextual understanding using sequence labeling and attention mechanisms:

#### Features:
- **Sequence labeling**: Labels each token with contextual toxicity information
- **Context-aware analysis**: Considers surrounding words and sentence structure
- **Attention weights**: Calculates importance weights for each token
- **Risk factor identification**: Identifies specific risk patterns
- **Multi-label classification**: Assigns multiple toxicity labels (TOXIC, AGGRESSIVE, etc.)

#### Usage:
```python
from contextual_analyzer import ContextualAnalyzer

analyzer = ContextualAnalyzer()
result = analyzer.analyze_text("You are so stupid")
# Returns detailed token-level analysis with sequence labels
```

### 4. Enhanced Detector Integration (`enhanced_detector.py`)

Unified system that combines all components using multi-task learning approach:

#### Features:
- **Multi-task learning**: Combines multiple analysis types with weighted scoring
- **Confidence aggregation**: Intelligently combines confidence scores
- **Fallback mechanism**: Gracefully handles component failures
- **Comprehensive reporting**: Provides detailed analysis results

## New API Endpoints

### Enhanced Detection
- **Endpoint**: `POST /api/detect`
- **Enhanced**: Returns additional fields when enhanced features are available:
  - `enhanced`: Boolean indicating if enhanced analysis was used
  - `normalized_text`: Text after normalization
  - `sarcasm_analysis`: Sarcasm detection results
  - `contextual_analysis`: Contextual analysis results
  - `analysis_summary`: Human-readable summary

### Text Normalization
- **Endpoint**: `POST /api/normalize`
- **Body**: `{"text": "ur message here"}`
- **Response**: 
  ```json
  {
    "original_text": "ur message here",
    "normalized_text": "your message here",
    "normalization_applied": true,
    "normalization_info": {...}
  }
  ```

### Sarcasm Detection
- **Endpoint**: `POST /api/detect_sarcasm`
- **Body**: `{"text": "Great job..."}`
- **Response**:
  ```json
  {
    "is_sarcastic": true,
    "confidence": 0.75,
    "confidence_level": "High",
    "indicators": ["great job", "punctuation_patterns"],
    "score_breakdown": {...}
  }
  ```

### Contextual Analysis
- **Endpoint**: `POST /api/analyze_context`
- **Body**: `{"text": "You are stupid"}`
- **Response**:
  ```json
  {
    "overall_toxicity": 0.65,
    "sequence_labels": [
      {"token": "you", "label": "OFFENSIVE", "confidence": 0.8},
      {"token": "are", "label": "NEUTRAL", "confidence": 0.1},
      {"token": "stupid", "label": "TOXIC", "confidence": 0.9}
    ],
    "risk_factors": ["Personal targeting detected"],
    "attention_weights": [0.8, 0.1, 0.9]
  }
  ```

### Health Check
- **Endpoint**: `GET /api/health`
- **Response**: Feature availability and model status

## Technical Improvements

### 1. Replaced Bag-of-Words with Contextual Embeddings

- **Before**: Simple word matching and basic pattern recognition
- **After**: Token-level contextual analysis considering surrounding context
- **Benefits**: Better understanding of context-dependent toxicity

### 2. Multi-Task Learning Approach

- **Integration**: Combines toxicity detection, sarcasm detection, and normalization
- **Weighted scoring**: Intelligently combines multiple confidence scores
- **Robustness**: Fallback mechanisms ensure continued operation

### 3. Sequence Labeling

- **Token-level analysis**: Each word gets individual toxicity assessment
- **Label types**: NEUTRAL, TOXIC, SARCASTIC, AGGRESSIVE, OFFENSIVE, THREATENING, DISCRIMINATORY
- **Context preservation**: Maintains word position and surrounding context information

## Testing

### Unit Tests
Run the enhanced feature tests:
```bash
cd backend
python test_enhanced_features.py
```

### API Tests
Test the enhanced API endpoints:
```bash
cd backend
python test_api.py
```

## Performance Considerations

### Graceful Degradation
- Enhanced features are optional - system falls back to original detection if unavailable
- Individual component failures don't break the entire system
- Compatible with existing API contracts

### Memory Usage
- Lightweight implementation without heavy model dependencies
- Efficient pattern matching and rule-based systems
- Minimal additional memory footprint

### Processing Speed
- Fast rule-based processing for normalization and sarcasm detection
- Efficient token-level analysis for contextual understanding
- Parallel processing capabilities for multiple analysis types

## Configuration

### Analysis Weights
The enhanced detector uses weighted combination of different analysis types:
- Original BERT: 40%
- Contextual analysis: 35%
- Sarcasm adjustment: 15%
- Normalization boost: 10%

### Thresholds
- Sarcasm detection threshold: 0.4
- Contextual toxicity threshold: 0.5
- Combined analysis threshold: 0.7 (configurable)

## Future Enhancements

### Planned Improvements
- [ ] Integration with additional pre-trained sarcasm detection models
- [ ] Advanced spelling correction using transformer models
- [ ] Real-time model fine-tuning based on feedback
- [ ] Multi-language support for normalization and sarcasm detection
- [ ] Advanced attention mechanisms for better contextual understanding

### Extensibility
- Modular design allows easy addition of new analysis components
- Plugin architecture for custom toxicity patterns
- Configurable weighting schemes for different use cases