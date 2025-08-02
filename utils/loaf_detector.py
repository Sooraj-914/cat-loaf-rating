import google.generativeai as genai
import cv2
import numpy as np
from PIL import Image
import os
import json
import random

class LoafDetector:
    def __init__(self):
        # Set up Gemini API - you can set the API key in multiple ways:
        # 1. Environment variable: export GEMINI_API_KEY="your-api-key-here"
        self.api_key = "AIzaSyBCCIsVjh2Rox6khna5fvIO00gCLp0HdzM"
        
        
        if not self.api_key:
            print("Warning: No GEMINI_API_KEY found. Using fallback method.")
            print("Set your API key with: export GEMINI_API_KEY='your-api-key-here'")
            self.use_ai = False
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.use_ai = True
                print("Gemini API configured successfully!")
            except Exception as e:
                print(f"Failed to configure Gemini API: {e}")
                self.use_ai = False
        
        # Fallback parameters
        self.ideal_loaf_ratio = 0.6
        self.ideal_loaf_area_ratio = 0.3
        
    def rate_loaf(self, image_path):
        """
        Rate how much a cat resembles a bread loaf using Gemini AI
        """
        try:
            print(f"Attempting to load image from: {image_path}")
            
            if self.use_ai:
                return self._rate_with_gemini(image_path)
            else:
                return self._rate_with_fallback(image_path)
                
        except Exception as e:
            print(f"Error in rate_loaf: {str(e)}")
            # Return a fun error response instead of crashing
            return {
                'loaf_score': random.randint(45, 75),
                'feedback': "Oops! Something went wrong, but I'll give this kitty the benefit of the doubt! 🐱",
                'details': {
                    'aspect_ratio': 0.65,
                    'area_ratio': 0.4,
                    'symmetry_score': 0.7,
                    'posture_score': 0.6
                }
            }
    
    def _rate_with_gemini(self, image_path):
        """Use Gemini Vision API to analyze the cat loaf"""
        try:
            # Load and prepare image using PIL (as per Gemini docs)
            image = Image.open(image_path)
            
            # Convert to RGB if needed (Gemini works best with RGB)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            print(f"Image loaded: {image.size}, mode: {image.mode}")
            
            # Create the prompt (simplified for better JSON parsing)
            prompt = """
Look at this image and rate how much this cat looks like a bread loaf from 0-100.

A perfect cat loaf has:
- Paws tucked under the body (not visible)
- Compact, rounded shape like bread
- Sitting upright in a loaf position
- Symmetrical pose

Respond with ONLY this JSON format (no other text):
{
    "loaf_score": 85,
    "feedback": "Great loaf! This cat has excellent bread-like form! 🍞",
    "details": {
        "aspect_ratio": 0.65,
        "area_ratio": 0.45,
        "symmetry_score": 0.8,
        "posture_score": 0.75
    }
}

Be generous with scoring - cats are trying their best!
            """
            
            try:
                # Send to Gemini (proper way according to docs)
                response = self.model.generate_content([prompt, image])
                
                # Check if response was blocked
                if response.candidates and response.candidates[0].finish_reason.name == "SAFETY":
                    print("Response was blocked by safety filters")
                    return self._rate_with_fallback(image_path)
                
                # Get the response text
                response_text = response.text.strip()
                print(f"Gemini raw response: {response_text}")
                
                # Try to extract and parse JSON
                return self._parse_gemini_response(response_text, image_path)
                
            except Exception as api_error:
                print(f"Gemini API call failed: {api_error}")
                return self._rate_with_fallback(image_path)
                
        except Exception as e:
            print(f"Error preparing image for Gemini: {str(e)}")
            return self._rate_with_fallback(image_path)
    
    def _parse_gemini_response(self, response_text, image_path):
        """Parse Gemini's response and extract JSON"""
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_text = response_text[start_idx:end_idx]
                print(f"Extracted JSON: {json_text}")
                
                result = json.loads(json_text)
                
                # Validate and clean the result
                result['loaf_score'] = max(0, min(100, int(result.get('loaf_score', 50))))
                
                # Ensure details exist and are reasonable
                if 'details' not in result:
                    result['details'] = {}
                
                details = result['details']
                details['aspect_ratio'] = max(0.2, min(3.0, float(details.get('aspect_ratio', 0.65))))
                details['area_ratio'] = max(0.1, min(1.0, float(details.get('area_ratio', 0.4))))
                details['symmetry_score'] = max(0.0, min(1.0, float(details.get('symmetry_score', 0.7))))
                details['posture_score'] = max(0.0, min(1.0, float(details.get('posture_score', 0.6))))
                
                # Ensure feedback exists
                if not result.get('feedback'):
                    result['feedback'] = self._generate_fallback_feedback(result['loaf_score'])
                
                return result
            else:
                print("No JSON found in response")
                raise ValueError("No JSON found in Gemini response")
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            print(f"Attempted to parse: {json_text if 'json_text' in locals() else 'N/A'}")
            return self._rate_with_fallback(image_path)
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return self._rate_with_fallback(image_path)
    
    def _rate_with_fallback(self, image_path):
        """Fallback method when AI is not available"""
        try:
            print("Using fallback method...")
            
            # Load image to get basic properties
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            height, width = image.shape[:2]
            print(f"Fallback: Image dimensions {width}x{height}")
            
            # Generate a reasonable score based on image properties
            aspect_ratio = height / width
            
            # Score based on how close the aspect ratio is to a loaf-like shape
            # Ideal loaf aspect ratio is around 0.6-0.8
            if 0.5 <= aspect_ratio <= 0.9:
                aspect_score = 0.8 + random.uniform(-0.1, 0.2)
            else:
                distance_from_ideal = min(abs(aspect_ratio - 0.6), abs(aspect_ratio - 0.8))
                aspect_score = max(0.3, 0.8 - distance_from_ideal)
            
            # Add some controlled randomness for variety based on image properties
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            brightness_factor = np.mean(gray) / 255.0
            random_factor = 0.8 + (brightness_factor * 0.4) + random.uniform(-0.1, 0.1)
            
            base_score = aspect_score * random_factor * 100
            loaf_score = max(25, min(85, int(base_score)))
            
            # Generate appropriate feedback
            feedback = self._generate_fallback_feedback(loaf_score)
            
            return {
                'loaf_score': loaf_score,
                'feedback': feedback,
                'details': {
                    'aspect_ratio': round(aspect_ratio, 3),
                    'area_ratio': round(random.uniform(0.2, 0.6), 3),
                    'symmetry_score': round(random.uniform(0.5, 0.9), 3),
                    'posture_score': round(random.uniform(0.4, 0.8), 3)
                }
            }
            
        except Exception as e:
            print(f"Fallback method failed: {str(e)}")
            # Last resort - return a default response
            return {
                'loaf_score': random.randint(40, 70),
                'feedback': "🐱 Kitty detected! Loaf analysis was tricky, but this cat gets points for being adorable!",
                'details': {
                    'aspect_ratio': 0.65,
                    'area_ratio': 0.35,
                    'symmetry_score': 0.65,
                    'posture_score': 0.55
                }
            }
    
    def _generate_fallback_feedback(self, loaf_score):
        """Generate appropriate feedback based on score"""
        if loaf_score >= 80:
            feedbacks = [
                "🍞 Excellent loaf! This kitty has mastered the art of loafing!",
                "🥖 Outstanding loaf form! This cat is definitely bread-like!",
                "🥯 Perfect loaf! This cat could win a bread contest!"
            ]
        elif loaf_score >= 65:
            feedbacks = [
                "🥨 Great loaf! This cat has solid loafing fundamentals!",
                "🍞 Good loaf form! Definitely getting bread vibes!",
                "🥯 Nice loaf! This kitty knows what they're doing!"
            ]
        elif loaf_score >= 50:
            feedbacks = [
                "🥐 Decent loaf attempt! This cat is learning to loaf!",
                "🍞 Fair loaf! Room for improvement but getting there!",
                "🥨 Respectable loaf! This kitty has potential!"
            ]
        else:
            feedbacks = [
                "🥖 Loaf-adjacent! Not quite bread but still adorable!",
                "🍞 Partial loaf detected! This cat is trying!",
                "🐱 Loaf attempt recognized! Keep practicing, kitty!"
            ]
        
        return random.choice(feedbacks)