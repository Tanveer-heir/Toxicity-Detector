#!/usr/bin/env python3
"""
Test script for enhanced toxicity detection features

This script tests the new features without requiring heavy model downloads.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from text_normalizer import TextNormalizer
from sarcasm_detector import SarcasmDetector
from contextual_analyzer import ContextualAnalyzer
from enhanced_detector import EnhancedToxicityDetector

def test_text_normalization():
    """Test text normalization functionality"""
    print("=== Testing Text Normalization ===")
    
    normalizer = TextNormalizer()
    
    test_cases = [
        "OMG ur sooooo stupid 😡 lol jk",
        "That's gr8! U should've seen it 2... 💯",
        "wtf is wrong w/ u??? 🤮",
        "luv u 2 death 💀 (not literally)",
        "dont b such an idiot!!!",
    ]
    
    for text in test_cases:
        normalized = normalizer.normalize_text(text)
        info = normalizer.get_normalization_info(text)
        
        print(f"\nOriginal: {text}")
        print(f"Normalized: {normalized}")
        print(f"Changed: {info['changed']}")
        if info['changed']:
            print(f"  Length: {info['original_length']} -> {info['normalized_length']}")
    
    print("\n✅ Text normalization tests completed")

def test_sarcasm_detection():
    """Test sarcasm detection functionality"""
    print("\n=== Testing Sarcasm Detection ===")
    
    detector = SarcasmDetector()
    
    test_cases = [
        "Oh really? How wonderful for you.",
        "Yeah right, that's totally believable.",
        "Great job on that presentation... 🙄",
        "WOW, so original!!!",
        "Thanks for nothing, buddy.",
        "This is just perfect... exactly what I needed.",
        "I love when things go wrong.",
        "Beautiful weather today.",  # Non-sarcastic
        "Thank you for your help!",  # Non-sarcastic
    ]
    
    for text in test_cases:
        result = detector.analyze_sarcasm(text)
        confidence_level = detector.get_sarcasm_confidence_level(result.confidence)
        
        print(f"\nText: {text}")
        print(f"Sarcastic: {result.is_sarcastic}")
        print(f"Confidence: {result.confidence:.3f} ({confidence_level})")
        if result.indicators:
            print(f"Indicators: {result.indicators[:3]}")  # Show first 3
    
    print("\n✅ Sarcasm detection tests completed")

def test_contextual_analysis():
    """Test contextual analysis functionality"""
    print("\n=== Testing Contextual Analysis ===")
    
    analyzer = ContextualAnalyzer()
    
    test_cases = [
        "You are so stupid it's unbelievable.",
        "I will kill you in the game tomorrow.",
        "Kill some time before the meeting.",
        "All those people are idiots.",
        "That's a stupid idea, sorry.",
        "Just a normal conversation here.",
    ]
    
    for text in test_cases:
        result = analyzer.analyze_text(text)
        
        print(f"\nText: {text}")
        print(f"Overall Toxicity: {result.overall_toxicity:.3f}")
        print(f"Risk Factors: {result.risk_factors}")
        
        # Show top 3 toxic tokens
        toxic_tokens = [t for t in result.sequence_labels if t.confidence > 0.3][:3]
        if toxic_tokens:
            print("Toxic tokens:")
            for token in toxic_tokens:
                print(f"  '{token.token}': {token.label.value} ({token.confidence:.3f})")
    
    print("\n✅ Contextual analysis tests completed")

def test_enhanced_detector():
    """Test the integrated enhanced detector"""
    print("\n=== Testing Enhanced Detector (without heavy models) ===")
    
    # Create detector without actual transformer models
    detector = EnhancedToxicityDetector(original_classifier=None, threshold=0.7)
    
    test_cases = [
        "ur such an idiot 😡 lol jk",
        "Great job... really amazing work 🙄",
        "I hate all those stupid people",
        "That's a nice day today",
        "wtf r u doing??? so annoying!!!",
    ]
    
    for text in test_cases:
        result = detector.analyze_toxicity_enhanced(text, set())
        summary = detector.get_analysis_summary(result)
        
        print(f"\nText: {text}")
        print(f"Overall Assessment: {summary['overall_assessment']}")
        print(f"Confidence: {summary['confidence']}")
        print(f"Sarcasm Detected: {summary['sarcasm_detected']}")
        print(f"Text Normalized: {summary['text_was_normalized']}")
        print(f"Risk Level: {summary['risk_level']}")
        print(f"Recommended Action: {summary['recommended_action']}")
        
        if result.normalization_applied:
            print(f"Normalized Text: {result.normalized_text}")
    
    print("\n✅ Enhanced detector tests completed")

def test_all():
    """Run all tests"""
    print("🧪 Starting Enhanced Toxicity Detection Tests\n")
    
    try:
        test_text_normalization()
        test_sarcasm_detection()
        test_contextual_analysis()
        test_enhanced_detector()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)