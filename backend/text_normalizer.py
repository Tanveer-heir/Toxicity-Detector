"""
Text Normalization Module for Enhanced Toxicity Detection

This module provides comprehensive text normalization including:
- Emoji to text conversion
- Slang and abbreviation expansion
- Spelling correction
- Enhanced preprocessing for contextual understanding
"""

import re
import unicodedata
from typing import Dict, List, Tuple, Optional

class TextNormalizer:
    """Advanced text normalizer for toxicity detection preprocessing"""
    
    def __init__(self):
        self.emoji_map = self._load_emoji_mappings()
        self.slang_map = self._load_slang_mappings()
        self.abbreviation_map = self._load_abbreviation_mappings()
        self.common_misspellings = self._load_misspelling_mappings()
    
    def _load_emoji_mappings(self) -> Dict[str, str]:
        """Load emoji to text mappings for normalization"""
        return {
            '😀': 'happy face',
            '😊': 'smiling face',
            '😂': 'laughing',
            '😍': 'heart eyes',
            '😎': 'cool',
            '😡': 'angry face',
            '😠': 'angry',
            '🤬': 'swearing',
            '💩': 'poop',
            '🖕': 'middle finger',
            '👎': 'thumbs down',
            '👍': 'thumbs up',
            '❤️': 'heart',
            '💔': 'broken heart',
            '🔥': 'fire',
            '💯': 'hundred percent',
            '🤮': 'vomiting',
            '🤢': 'nauseated',
            '😤': 'huffing',
            '😭': 'crying',
            '🙄': 'eye roll',
            '😏': 'smirk',
            '😈': 'devil',
            '👹': 'monster',
            '💀': 'skull',
            '☠️': 'skull and crossbones'
        }
    
    def _load_slang_mappings(self) -> Dict[str, str]:
        """Load slang to standard text mappings"""
        return {
            # Internet slang
            'lol': 'laugh out loud',
            'lmao': 'laughing my ass off',
            'rofl': 'rolling on floor laughing',
            'wtf': 'what the fuck',
            'omg': 'oh my god',
            'fml': 'fuck my life',
            'smh': 'shaking my head',
            'tbh': 'to be honest',
            'imo': 'in my opinion',
            'imho': 'in my humble opinion',
            'afaik': 'as far as I know',
            'tl;dr': 'too long did not read',
            'brb': 'be right back',
            'gtg': 'got to go',
            'ttyl': 'talk to you later',
            'irl': 'in real life',
            'ngl': 'not gonna lie',
            'fr': 'for real',
            'periodt': 'period',
            'salty': 'bitter or angry',
            'lit': 'excellent or exciting',
            'fire': 'excellent',
            'sus': 'suspicious',
            'cap': 'lie',
            'no cap': 'no lie',
            'facts': 'truth',
            'bet': 'yes or okay',
            'vibes': 'feelings or atmosphere',
            'flex': 'show off',
            'stan': 'obsessive fan',
            'simp': 'someone who does too much for someone they like',
            'karen': 'entitled demanding person',
            'boomer': 'older person',
            'zoomer': 'young person',
            'millennial': 'person born 1981-1996',
            # Offensive slang transformations
            'mofo': 'motherfucker',
            'pos': 'piece of shit',
            'sob': 'son of a bitch',
            'mf': 'motherfucker',
            'prick': 'jerk',
            'douche': 'jerk',
            'tard': 'idiot'
        }
    
    def _load_abbreviation_mappings(self) -> Dict[str, str]:
        """Load abbreviation to full form mappings"""
        return {
            'u': 'you',
            'ur': 'your',
            'r': 'are',
            'n': 'and',
            'w/': 'with',
            'w/o': 'without',
            'b4': 'before',
            '2': 'to',
            '4': 'for',
            '8': 'ate',
            'c': 'see',
            'y': 'why',
            'bc': 'because',
            'bcuz': 'because',
            'cuz': 'because',
            'luv': 'love',
            'gud': 'good',
            'gr8': 'great',
            'thru': 'through',
            'ppl': 'people',
            'plz': 'please',
            'thx': 'thanks',
            'thanx': 'thanks',
            'tho': 'though',
            'altho': 'although',
            'gonna': 'going to',
            'wanna': 'want to',
            'gotta': 'got to',
            'kinda': 'kind of',
            'sorta': 'sort of',
            'outta': 'out of',
            'shoulda': 'should have',
            'coulda': 'could have',
            'woulda': 'would have'
        }
    
    def _load_misspelling_mappings(self) -> Dict[str, str]:
        """Load common misspelling corrections"""
        return {
            'recieve': 'receive',
            'seperate': 'separate',
            'definately': 'definitely',
            'alot': 'a lot',
            'teh': 'the',
            'thier': 'their',
            'thats': 'that is',
            'its': 'it is',
            'youre': 'you are',
            'dont': 'do not',
            'cant': 'can not',
            'wont': 'will not',
            'isnt': 'is not',
            'arent': 'are not',
            'wasnt': 'was not',
            'werent': 'were not',
            'hasnt': 'has not',
            'havent': 'have not',
            'hadnt': 'had not',
            'shouldnt': 'should not',
            'couldnt': 'could not',
            'wouldnt': 'would not',
            'mustnt': 'must not'
        }
    
    def normalize_emojis(self, text: str) -> str:
        """Convert emojis to their text representations"""
        normalized_text = text
        for emoji, description in self.emoji_map.items():
            normalized_text = normalized_text.replace(emoji, f" {description} ")
        return normalized_text
    
    def expand_slang(self, text: str) -> str:
        """Expand slang terms to their full meanings"""
        words = text.split()
        expanded_words = []
        
        for word in words:
            # Remove punctuation for matching but preserve it
            clean_word = re.sub(r'[^\w]', '', word.lower())
            punctuation = ''.join(re.findall(r'[^\w]', word))
            
            if clean_word in self.slang_map:
                expanded_words.append(self.slang_map[clean_word] + punctuation)
            else:
                expanded_words.append(word)
        
        return ' '.join(expanded_words)
    
    def expand_abbreviations(self, text: str) -> str:
        """Expand common abbreviations"""
        words = text.split()
        expanded_words = []
        
        for word in words:
            # Remove punctuation for matching but preserve it
            clean_word = re.sub(r'[^\w]', '', word.lower())
            punctuation = ''.join(re.findall(r'[^\w]', word))
            
            if clean_word in self.abbreviation_map:
                expanded_words.append(self.abbreviation_map[clean_word] + punctuation)
            else:
                expanded_words.append(word)
        
        return ' '.join(expanded_words)
    
    def correct_spelling(self, text: str) -> str:
        """Correct common misspellings"""
        words = text.split()
        corrected_words = []
        
        for word in words:
            # Remove punctuation for matching but preserve it
            clean_word = re.sub(r'[^\w]', '', word.lower())
            punctuation = ''.join(re.findall(r'[^\w]', word))
            
            if clean_word in self.common_misspellings:
                corrected_words.append(self.common_misspellings[clean_word] + punctuation)
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)
    
    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace and remove extra spaces"""
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def normalize_case(self, text: str) -> str:
        """Normalize case - handle excessive caps"""
        words = text.split()
        normalized_words = []
        
        for word in words:
            # If word is all caps and longer than 2 characters, convert to lowercase
            if len(word) > 2 and word.isupper():
                normalized_words.append(word.lower())
            else:
                normalized_words.append(word)
        
        return ' '.join(normalized_words)
    
    def remove_repeated_chars(self, text: str) -> str:
        """Remove excessive repeated characters (e.g., 'sooooo' -> 'so')"""
        # Replace 3+ repeated characters with 2
        return re.sub(r'(.)\1{2,}', r'\1\1', text)
    
    def normalize_text(self, text: str) -> str:
        """
        Apply comprehensive text normalization
        
        Args:
            text: Raw input text
            
        Returns:
            Normalized text ready for analysis
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Step 1: Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        # Step 2: Convert emojis to text
        text = self.normalize_emojis(text)
        
        # Step 3: Expand slang and abbreviations
        text = self.expand_slang(text)
        text = self.expand_abbreviations(text)
        
        # Step 4: Correct spelling
        text = self.correct_spelling(text)
        
        # Step 5: Normalize case
        text = self.normalize_case(text)
        
        # Step 6: Remove repeated characters
        text = self.remove_repeated_chars(text)
        
        # Step 7: Normalize whitespace
        text = self.normalize_whitespace(text)
        
        return text
    
    def get_normalization_info(self, original_text: str) -> Dict[str, any]:
        """
        Get detailed information about normalization steps applied
        
        Args:
            original_text: Original input text
            
        Returns:
            Dictionary with normalization steps and results
        """
        steps = {}
        current_text = original_text
        
        # Track each normalization step
        steps['original'] = current_text
        
        current_text = self.normalize_emojis(current_text)
        steps['emoji_normalized'] = current_text
        
        current_text = self.expand_slang(current_text)
        steps['slang_expanded'] = current_text
        
        current_text = self.expand_abbreviations(current_text)
        steps['abbreviations_expanded'] = current_text
        
        current_text = self.correct_spelling(current_text)
        steps['spelling_corrected'] = current_text
        
        current_text = self.normalize_case(current_text)
        steps['case_normalized'] = current_text
        
        current_text = self.remove_repeated_chars(current_text)
        steps['repeated_chars_removed'] = current_text
        
        current_text = self.normalize_whitespace(current_text)
        steps['final_normalized'] = current_text
        
        return {
            'steps': steps,
            'changed': steps['original'] != steps['final_normalized'],
            'original_length': len(original_text),
            'normalized_length': len(current_text)
        }