#!/usr/bin/env python3
"""
Enhanced Matching Engine for Multi-Angle Face Detection System

Matches face encodings against database with multi-angle support and weighted confidence scoring.
Implements optimized matching algorithms with caching and vectorization.

Features:
- Single-angle matching
- Multi-angle matching with quality weighting
- Confidence scoring with angle-based weights
- Performance optimization with caching
- Euclidean distance calculation
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from multi_angle_database import MultiAngleFaceDatabase
import time

class EnhancedMatchingEngine:
    """
    Enhanced matching engine with multi-angle support
    """
    
    # Angle-based weights for matching confidence
    ANGLE_WEIGHTS = {
        'frontal': 1.0,
        'left_45': 0.8,
        'right_45': 0.8,
        'left_90': 0.6,
        'right_90': 0.6
    }
    
    def __init__(self, database: MultiAngleFaceDatabase, threshold: float = 0.6):
        """
        Initialize matching engine
        
        Args:
            database: MultiAngleFaceDatabase instance
            threshold: Match distance threshold (default 0.6)
        """
        self.database = database
        self.threshold = threshold
        self.encoding_cache = {}
        self.cache_timestamp = 0
        self.cache_ttl = 300  # Cache time-to-live in seconds (5 minutes)
        
        print("=" * 70)
        print("INITIALIZING ENHANCED MATCHING ENGINE")
        print("=" * 70)
        print(f"  Match threshold: {threshold}")
        print(f"  Angle weights: {self.ANGLE_WEIGHTS}")
        print("✓ Enhanced Matching Engine initialized successfully")
        print("=" * 70)
        print()
    
    def match_face(self, encoding: np.ndarray, angle: Optional[str] = None) -> Dict:
        """
        Match single encoding against database
        
        Args:
            encoding: 128D encoding to match
            angle: Optional angle hint for optimization
            
        Returns:
            Match result with person_id, confidence, distance, or None if no match
        """
        # Validate encoding
        if encoding.shape[0] != 128:
            raise ValueError(f"Encoding must be 128D, got {encoding.shape[0]}D")
        
        # Get all encodings from database (with caching)
        all_encodings = self._get_cached_encodings()
        
        if not all_encodings:
            return {
                'matched': False,
                'person_id': None,
                'confidence': 0.0,
                'distance': float('inf'),
                'message': 'No encodings in database'
            }
        
        # Calculate distances to all encodings
        best_match = None
        best_distance = float('inf')
        
        for enc_record in all_encodings:
            # Calculate Euclidean distance
            stored_encoding = enc_record['encoding_array']
            distance = np.linalg.norm(encoding - stored_encoding)
            
            # Apply angle weight if angle hint provided
            if angle and enc_record['angle'] == angle:
                # Boost matches with same angle
                distance *= 0.9
            
            # Track best match
            if distance < best_distance:
                best_distance = distance
                best_match = enc_record
        
        # Check if match is below threshold
        if best_distance < self.threshold and best_match:
            # Calculate confidence score
            confidence = self._distance_to_confidence(best_distance)
            
            # Apply quality weight
            quality_weight = float(best_match['quality_score'])
            weighted_confidence = 0.7 * confidence + 0.3 * quality_weight
            
            return {
                'matched': True,
                'person_id': best_match['person_id'],
                'confidence': weighted_confidence,
                'distance': best_distance,
                'angle': best_match['angle'],
                'quality_score': quality_weight,
                'encoding_id': best_match['id']
            }
        else:
            return {
                'matched': False,
                'person_id': None,
                'confidence': 0.0,
                'distance': best_distance,
                'message': f'No match found (best distance: {best_distance:.3f})'
            }
    
    def match_multi_angle(self, encodings: Dict[str, np.ndarray]) -> Dict:
        """
        Match multiple angles simultaneously
        
        Args:
            encodings: Dictionary mapping angles to encodings
            
        Returns:
            Best match result with weighted confidence
        """
        if not encodings:
            return {
                'matched': False,
                'person_id': None,
                'confidence': 0.0,
                'message': 'No encodings provided'
            }
        
        # Get all encodings from database
        all_encodings = self._get_cached_encodings()
        
        if not all_encodings:
            return {
                'matched': False,
                'person_id': None,
                'confidence': 0.0,
                'message': 'No encodings in database'
            }
        
        # Group database encodings by person
        person_encodings = {}
        for enc in all_encodings:
            person_id = enc['person_id']
            if person_id not in person_encodings:
                person_encodings[person_id] = []
            person_encodings[person_id].append(enc)
        
        # Match against each person
        best_person_match = None
        best_person_confidence = 0.0
        
        for person_id, person_encs in person_encodings.items():
            # Calculate match scores for this person
            match_scores = []
            
            for query_angle, query_encoding in encodings.items():
                # Find best match for this angle
                best_angle_distance = float('inf')
                best_angle_quality = 0.0
                
                for stored_enc in person_encs:
                    distance = np.linalg.norm(query_encoding - stored_enc['encoding_array'])
                    
                    if distance < best_angle_distance:
                        best_angle_distance = distance
                        best_angle_quality = float(stored_enc['quality_score'])
                
                # Calculate weighted score for this angle
                if best_angle_distance < self.threshold:
                    angle_weight = self.ANGLE_WEIGHTS.get(query_angle, 0.5)
                    confidence = self._distance_to_confidence(best_angle_distance)
                    weighted_score = angle_weight * (0.7 * confidence + 0.3 * best_angle_quality)
                    
                    match_scores.append({
                        'angle': query_angle,
                        'distance': best_angle_distance,
                        'confidence': confidence,
                        'quality': best_angle_quality,
                        'weighted_score': weighted_score
                    })
            
            # Calculate overall confidence for this person
            if match_scores:
                # Average weighted scores
                person_confidence = np.mean([s['weighted_score'] for s in match_scores])
                
                if person_confidence > best_person_confidence:
                    best_person_confidence = person_confidence
                    best_person_match = {
                        'person_id': person_id,
                        'confidence': person_confidence,
                        'match_scores': match_scores,
                        'num_angles_matched': len(match_scores)
                    }
        
        # Return best match
        if best_person_match and best_person_confidence > 0.5:
            return {
                'matched': True,
                **best_person_match
            }
        else:
            return {
                'matched': False,
                'person_id': None,
                'confidence': best_person_confidence,
                'message': f'No confident match (best confidence: {best_person_confidence:.3f})'
            }
    
    def calculate_confidence(self, distances: List[float], qualities: List[float], 
                           angles: List[str]) -> float:
        """
        Calculate weighted match confidence
        
        Args:
            distances: List of encoding distances
            qualities: List of encoding quality scores
            angles: List of angle classifications
            
        Returns:
            Weighted confidence score (0-1)
        """
        if not distances or len(distances) != len(qualities) or len(distances) != len(angles):
            return 0.0
        
        weighted_scores = []
        
        for distance, quality, angle in zip(distances, qualities, angles):
            # Convert distance to confidence
            confidence = self._distance_to_confidence(distance)
            
            # Apply angle weight
            angle_weight = self.ANGLE_WEIGHTS.get(angle, 0.5)
            
            # Combine confidence and quality
            weighted_score = angle_weight * (0.7 * confidence + 0.3 * quality)
            weighted_scores.append(weighted_score)
        
        # Return average weighted score
        return float(np.mean(weighted_scores))
    
    def batch_match(self, encodings: List[np.ndarray], angles: Optional[List[str]] = None) -> List[Dict]:
        """
        Match multiple encodings in batch
        
        Args:
            encodings: List of 128D encodings
            angles: Optional list of angle hints
            
        Returns:
            List of match results
        """
        results = []
        
        for i, encoding in enumerate(encodings):
            angle = angles[i] if angles and i < len(angles) else None
            result = self.match_face(encoding, angle)
            results.append(result)
        
        return results
    
    def find_similar_faces(self, encoding: np.ndarray, top_k: int = 5) -> List[Dict]:
        """
        Find top K most similar faces
        
        Args:
            encoding: 128D encoding to match
            top_k: Number of results to return
            
        Returns:
            List of top K matches sorted by distance
        """
        all_encodings = self._get_cached_encodings()
        
        if not all_encodings:
            return []
        
        # Calculate distances to all encodings
        matches = []
        
        for enc_record in all_encodings:
            stored_encoding = enc_record['encoding_array']
            distance = np.linalg.norm(encoding - stored_encoding)
            
            matches.append({
                'person_id': enc_record['person_id'],
                'distance': distance,
                'confidence': self._distance_to_confidence(distance),
                'angle': enc_record['angle'],
                'quality_score': float(enc_record['quality_score'])
            })
        
        # Sort by distance and return top K
        matches.sort(key=lambda x: x['distance'])
        return matches[:top_k]
    
    def _distance_to_confidence(self, distance: float) -> float:
        """
        Convert Euclidean distance to confidence score (0-1)
        
        Args:
            distance: Euclidean distance
            
        Returns:
            Confidence score (0-1)
        """
        # Use exponential decay: confidence = e^(-distance)
        # This gives confidence of ~0.55 at threshold 0.6
        confidence = np.exp(-distance)
        return float(np.clip(confidence, 0.0, 1.0))
    
    def _get_cached_encodings(self) -> List[Dict]:
        """
        Get all encodings with caching
        
        Returns:
            List of encoding records
        """
        current_time = time.time()
        
        # Check if cache is valid
        if self.encoding_cache and (current_time - self.cache_timestamp) < self.cache_ttl:
            return self.encoding_cache
        
        # Refresh cache
        self.encoding_cache = self.database.get_all_encodings()
        self.cache_timestamp = current_time
        
        return self.encoding_cache
    
    def clear_cache(self):
        """Clear encoding cache"""
        self.encoding_cache = {}
        self.cache_timestamp = 0
        print("✓ Encoding cache cleared")
    
    def get_statistics(self) -> Dict:
        """Get matching engine statistics"""
        all_encodings = self._get_cached_encodings()
        
        # Count encodings by angle
        angle_counts = {}
        for enc in all_encodings:
            angle = enc['angle']
            angle_counts[angle] = angle_counts.get(angle, 0) + 1
        
        # Count unique persons
        unique_persons = len(set(enc['person_id'] for enc in all_encodings))
        
        return {
            'total_encodings': len(all_encodings),
            'unique_persons': unique_persons,
            'angle_distribution': angle_counts,
            'cache_size': len(self.encoding_cache),
            'cache_age_seconds': time.time() - self.cache_timestamp if self.cache_timestamp else 0,
            'threshold': self.threshold
        }


def main():
    """Test the Enhanced Matching Engine"""
    print("\n" + "=" * 70)
    print("TESTING ENHANCED MATCHING ENGINE")
    print("=" * 70)
    
    # Initialize database and matching engine
    from multi_angle_database import MultiAngleFaceDatabase
    
    db = MultiAngleFaceDatabase()
    engine = EnhancedMatchingEngine(db, threshold=0.6)
    
    # Get statistics
    print("\nMatching Engine Statistics:")
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Close database
    db.close()
    
    print("\n✓ Enhanced Matching Engine test complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
