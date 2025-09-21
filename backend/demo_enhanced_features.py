#!/usr/bin/env python3
"""
Enhanced Toxicity Detection Demo

This script demonstrates the new enhanced features for toxicity detection.
It shows how the system now handles sarcasm, text normalization, and contextual analysis.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from text_normalizer import TextNormalizer
from sarcasm_detector import SarcasmDetector
from contextual_analyzer import ContextualAnalyzer
from enhanced_detector import EnhancedToxicityDetector

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def demo_text_normalization():
    """Demonstrate text normalization capabilities"""
    print_header("TEXT NORMALIZATION DEMO")
    
    normalizer = TextNormalizer()
    
    examples = [
        "OMG ur sooooo stupid 😡 lol jk dont b mad",
        "wtf r u doing??? thats gr8! 💯",
        "i luv u 2 death 💀 (not literally tho)",
        "STOP YELLING!!! its soooo annoying 🙄",
        "bcuz ur such a gud friend 😊"
    ]
    
    print("Converting informal text to normalized form:\n")
    
    for i, text in enumerate(examples, 1):
        normalized = normalizer.normalize_text(text)
        print(f"{i}. Original:   '{text}'")
        print(f"   Normalized: '{normalized}'")
        print()

def demo_sarcasm_detection():
    """Demonstrate sarcasm and irony detection"""
    print_header("SARCASM & IRONY DETECTION DEMO")
    
    detector = SarcasmDetector()
    
    examples = [
        ("Oh really? How wonderful for you.", "Basic sarcasm"),
        ("Yeah right, that's totally believable.", "Dismissive sarcasm"),
        ("Great job... really amazing work 🙄", "Sarcasm with emoji"),
        ("WOW, so original!!!", "Exaggerated sarcasm"),
        ("Thanks for nothing, buddy.", "Sarcastic thanks"),
        ("I just LOVE when things go wrong.", "Ironic statement"),
        ("Beautiful weather today!", "Non-sarcastic (control)"),
        ("Thank you for your help!", "Genuine appreciation (control)")
    ]
    
    print("Analyzing text for sarcasm and irony:\n")
    
    for text, description in examples:
        result = detector.analyze_sarcasm(text)
        confidence_level = detector.get_sarcasm_confidence_level(result.confidence)
        
        status = "🎭 SARCASTIC" if result.is_sarcastic else "😊 GENUINE"
        
        print(f"Text: '{text}'")
        print(f"Type: {description}")
        print(f"Result: {status} (confidence: {result.confidence:.3f} - {confidence_level})")
        if result.indicators:
            print(f"Indicators: {', '.join(result.indicators[:3])}")
        print()

def demo_contextual_analysis():
    """Demonstrate contextual analysis with sequence labeling"""
    print_header("CONTEXTUAL ANALYSIS DEMO")
    
    analyzer = ContextualAnalyzer()
    
    examples = [
        ("You are so stupid it's unbelievable.", "Personal attack"),
        ("I will kill you in the game tomorrow.", "Gaming context"),
        ("Kill some time before the meeting.", "Metaphorical usage"),
        ("All those people are complete idiots.", "Group targeting"),
        ("That's a really stupid idea, sorry.", "Idea criticism"),
        ("What a beautiful day today!", "Positive statement")
    ]
    
    print("Analyzing text with contextual understanding:\n")
    
    for text, description in examples:
        result = analyzer.analyze_text(text)
        
        print(f"Text: '{text}'")
        print(f"Context: {description}")
        print(f"Overall Toxicity: {result.overall_toxicity:.3f}")
        
        # Show the most toxic tokens
        toxic_tokens = [t for t in result.sequence_labels if t.confidence > 0.3][:3]
        if toxic_tokens:
            print("Key toxic elements:")
            for token in toxic_tokens:
                print(f"  → '{token.token}': {token.label.value} (confidence: {token.confidence:.3f})")
        
        if result.risk_factors:
            print(f"Risk factors: {', '.join(result.risk_factors)}")
        
        print()

def demo_enhanced_detection():
    """Demonstrate the integrated enhanced detection system"""
    print_header("ENHANCED DETECTION INTEGRATION DEMO")
    
    # Create detector without heavy models for demo
    detector = EnhancedToxicityDetector(original_classifier=None, threshold=0.7)
    
    examples = [
        ("ur such an idiot 😡 lol jk", "Normalized toxic text with humor disclaimer"),
        ("Great job... really amazing work 🙄", "Sarcastic praise"),
        ("I hate all those stupid people", "Direct hate speech"),
        ("wtf r u doing??? so annoying!!!", "Aggressive informal text"),
        ("That's a beautiful day today", "Positive control"),
        ("OMG thx soooo much!!! 💖", "Positive informal text")
    ]
    
    print("Complete enhanced analysis combining all features:\n")
    
    for text, description in examples:
        result = detector.analyze_toxicity_enhanced(text, set())
        summary = detector.get_analysis_summary(result)
        
        print(f"Text: '{text}'")
        print(f"Context: {description}")
        print(f"Assessment: {summary['overall_assessment']} (confidence: {summary['confidence']})")
        print(f"Risk Level: {summary['risk_level']}")
        print(f"Recommended Action: {summary['recommended_action']}")
        
        features = []
        if result.normalization_applied:
            features.append(f"Normalized: '{result.normalized_text}'")
        if result.is_sarcastic:
            features.append(f"Sarcasm detected ({result.sarcasm_confidence:.3f})")
        if result.risk_factors:
            features.append(f"Risk factors: {', '.join(result.risk_factors[:2])}")
        
        if features:
            print(f"Details: {' | '.join(features)}")
        
        print()

def main():
    """Run complete demo of enhanced features"""
    print("🤖 Enhanced Toxicity Detection System Demo")
    print("This demo showcases the new advanced features for handling:")
    print("• Text normalization (slang, emojis, spelling)")
    print("• Sarcasm and irony detection")
    print("• Contextual analysis with sequence labeling")
    print("• Multi-task learning integration")
    
    try:
        demo_text_normalization()
        demo_sarcasm_detection()
        demo_contextual_analysis()
        demo_enhanced_detection()
        
        print_header("DEMO COMPLETE")
        print("✨ All enhanced features demonstrated successfully!")
        print("\nKey improvements achieved:")
        print("✅ Replaced bag-of-words with contextual token analysis")
        print("✅ Added specialized sarcasm and irony detection")
        print("✅ Implemented comprehensive text normalization")
        print("✅ Created multi-task learning integration")
        print("✅ Added sequence labeling for better context understanding")
        
        print(f"\n📚 See ENHANCED_FEATURES.md for detailed documentation")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)