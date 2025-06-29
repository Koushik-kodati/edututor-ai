import os
from typing import List, Dict
from langchain_ibm import WatsonxLLM
from langchain.prompts import PromptTemplate
import json
import logging

logger = logging.getLogger(__name__)

class WatsonxService:
    def __init__(self):
        self.model_id = os.getenv("WATSONX_MODEL_ID", "ibm-granite/granite-3.3-2b-instruct")
        self.api_key = os.getenv("WATSONX_APIKEY")
        self.project_id = os.getenv("WATSONX_PROJECT_ID")
        self.endpoint = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        
        if not all([self.api_key, self.project_id]):
            logger.warning("Watsonx credentials not found, using enhanced mock responses")
            self.llm = None
        else:
            try:
                self.llm = WatsonxLLM(
                    model_id=self.model_id,
                    url=self.endpoint,
                    apikey=self.api_key,
                    project_id=self.project_id,
                    params={
                        "decoding_method": "greedy",
                        "max_new_tokens": 2000,
                        "temperature": 0.7,
                        "repetition_penalty": 1.1
                    }
                )
                logger.info("✅ IBM Watsonx initialized successfully with Granite model!")
            except Exception as e:
                logger.error(f"Failed to initialize Watsonx: {e}")
                self.llm = None

    def generate_quiz_questions(self, topic: str, difficulty: str, num_questions: int = 5) -> List[Dict]:
        """Generate quiz questions using IBM Granite model"""
        
        if not self.llm:
            logger.info("Using enhanced mock questions for development")
            return self._get_enhanced_mock_questions(topic, difficulty, num_questions)
        
        try:
            prompt_template = PromptTemplate(
                input_variables=["topic", "difficulty", "num_questions"],
                template="""
                You are an expert educational content creator. Generate {num_questions} high-quality multiple choice questions about {topic} at {difficulty} difficulty level.

                Requirements:
                1. Each question must be clear, educational, and appropriate for the difficulty level
                2. Provide exactly 4 answer options (A, B, C, D)
                3. Include a brief explanation for the correct answer
                4. Questions should test understanding, not just memorization
                5. Ensure questions are factually accurate and well-researched

                Topic: {topic}
                Difficulty: {difficulty}
                Number of questions: {num_questions}

                Format your response as a valid JSON array with this exact structure:
                [
                  {{
                    "question": "What is the capital of France?",
                    "options": ["London", "Berlin", "Paris", "Madrid"],
                    "correct_answer": 2,
                    "explanation": "Paris is the capital and largest city of France, located in the north-central part of the country."
                  }}
                ]

                Generate {num_questions} questions now:
                """
            )
            
            prompt = prompt_template.format(
                topic=topic,
                difficulty=difficulty,
                num_questions=num_questions
            )
            
            logger.info(f"Generating {num_questions} questions for {topic} ({difficulty}) using IBM Granite AI")
            response = self.llm.invoke(prompt)
            
            # Parse the JSON response
            try:
                # Clean the response to extract JSON
                response_clean = response.strip()
                if response_clean.startswith('```json'):
                    response_clean = response_clean[7:]
                if response_clean.endswith('```'):
                    response_clean = response_clean[:-3]
                
                questions = json.loads(response_clean)
                
                if isinstance(questions, list) and len(questions) > 0:
                    # Validate question format
                    validated_questions = []
                    for q in questions:
                        if self._validate_question(q):
                            validated_questions.append(q)
                    
                    if validated_questions:
                        logger.info(f"Successfully generated {len(validated_questions)} questions using IBM Granite AI")
                        return validated_questions
                    else:
                        logger.warning("No valid questions in Watsonx response, using mock questions")
                        return self._get_enhanced_mock_questions(topic, difficulty, num_questions)
                else:
                    logger.warning("Invalid response format from Watsonx, using mock questions")
                    return self._get_enhanced_mock_questions(topic, difficulty, num_questions)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response from Watsonx: {e}")
                logger.debug(f"Raw response: {response}")
                return self._get_enhanced_mock_questions(topic, difficulty, num_questions)
                
        except Exception as e:
            logger.error(f"Error generating questions with Watsonx: {e}")
            return self._get_enhanced_mock_questions(topic, difficulty, num_questions)

    def _validate_question(self, question: Dict) -> bool:
        """Validate question format"""
        required_fields = ['question', 'options', 'correct_answer', 'explanation']
        
        if not all(field in question for field in required_fields):
            return False
        
        if not isinstance(question['options'], list) or len(question['options']) != 4:
            return False
        
        if not isinstance(question['correct_answer'], int) or question['correct_answer'] not in [0, 1, 2, 3]:
            return False
        
        return True

    def _get_enhanced_mock_questions(self, topic: str, difficulty: str, num_questions: int) -> List[Dict]:
        """Enhanced mock questions with better variety and quality"""
        
        mock_questions = {
            "Mathematics": {
                "easy": [
                    {
                        "question": "What is 15 + 27?",
                        "options": ["40", "42", "44", "46"],
                        "correct_answer": 1,
                        "explanation": "15 + 27 = 42. This is basic addition."
                    },
                    {
                        "question": "What is 8 × 7?",
                        "options": ["54", "56", "58", "60"],
                        "correct_answer": 1,
                        "explanation": "8 × 7 = 56. This is a basic multiplication fact."
                    },
                    {
                        "question": "What is 100 ÷ 4?",
                        "options": ["20", "25", "30", "35"],
                        "correct_answer": 1,
                        "explanation": "100 ÷ 4 = 25. Division is the inverse of multiplication."
                    },
                    {
                        "question": "What is the area of a rectangle with length 6 and width 4?",
                        "options": ["20", "24", "28", "32"],
                        "correct_answer": 1,
                        "explanation": "Area = length × width = 6 × 4 = 24 square units."
                    },
                    {
                        "question": "What is 50% of 80?",
                        "options": ["30", "35", "40", "45"],
                        "correct_answer": 2,
                        "explanation": "50% of 80 = 0.5 × 80 = 40."
                    }
                ],
                "medium": [
                    {
                        "question": "What is the derivative of x²?",
                        "options": ["2x", "x²", "2", "x"],
                        "correct_answer": 0,
                        "explanation": "Using the power rule: d/dx(x²) = 2x¹ = 2x"
                    },
                    {
                        "question": "What is the integral of 2x dx?",
                        "options": ["x²", "x² + C", "2", "2x + C"],
                        "correct_answer": 1,
                        "explanation": "∫2x dx = x² + C, where C is the constant of integration"
                    },
                    {
                        "question": "What is the value of sin(π/2)?",
                        "options": ["0", "1", "-1", "π/2"],
                        "correct_answer": 1,
                        "explanation": "sin(π/2) = sin(90°) = 1"
                    },
                    {
                        "question": "Solve for x: 2x + 5 = 13",
                        "options": ["x = 4", "x = 6", "x = 8", "x = 9"],
                        "correct_answer": 0,
                        "explanation": "2x = 13 - 5 = 8, so x = 4"
                    },
                    {
                        "question": "What is the area of a circle with radius 3?",
                        "options": ["6π", "9π", "12π", "18π"],
                        "correct_answer": 1,
                        "explanation": "Area = πr² = π(3)² = 9π"
                    }
                ],
                "hard": [
                    {
                        "question": "What is the limit of (sin x)/x as x approaches 0?",
                        "options": ["0", "1", "∞", "undefined"],
                        "correct_answer": 1,
                        "explanation": "This is a fundamental limit: lim(x→0) (sin x)/x = 1"
                    },
                    {
                        "question": "What is the Taylor series expansion of e^x around x = 0?",
                        "options": ["1 + x + x²/2! + x³/3! + ...", "x + x²/2 + x³/3 + ...", "1 + x + x² + x³ + ...", "x + x² + x³ + ..."],
                        "correct_answer": 0,
                        "explanation": "The Taylor series for e^x is: e^x = Σ(x^n/n!) = 1 + x + x²/2! + x³/3! + ..."
                    },
                    {
                        "question": "What is the eigenvalue equation for a matrix A?",
                        "options": ["Av = λv", "A + v = λv", "Av = v + λ", "A - v = λ"],
                        "correct_answer": 0,
                        "explanation": "The eigenvalue equation is Av = λv, where λ is the eigenvalue and v is the eigenvector"
                    }
                ]
            },
            "Physics": {
                "easy": [
                    {
                        "question": "What is the unit of force?",
                        "options": ["Joule", "Newton", "Watt", "Pascal"],
                        "correct_answer": 1,
                        "explanation": "The Newton (N) is the SI unit of force, named after Isaac Newton."
                    },
                    {
                        "question": "What is the speed of light in vacuum?",
                        "options": ["3 × 10⁸ m/s", "3 × 10⁶ m/s", "3 × 10¹⁰ m/s", "3 × 10⁴ m/s"],
                        "correct_answer": 0,
                        "explanation": "The speed of light in vacuum is approximately 3 × 10⁸ meters per second"
                    },
                    {
                        "question": "What happens to an object in free fall (ignoring air resistance)?",
                        "options": ["It accelerates upward", "It moves at constant speed", "It accelerates downward", "It decelerates"],
                        "correct_answer": 2,
                        "explanation": "Objects in free fall accelerate downward due to gravity at approximately 9.8 m/s²"
                    }
                ],
                "medium": [
                    {
                        "question": "What is Newton's second law of motion?",
                        "options": ["F = ma", "E = mc²", "v = u + at", "s = ut + ½at²"],
                        "correct_answer": 0,
                        "explanation": "Newton's second law states that Force equals mass times acceleration"
                    },
                    {
                        "question": "What is the unit of electric current?",
                        "options": ["Volt", "Ampere", "Ohm", "Watt"],
                        "correct_answer": 1,
                        "explanation": "The ampere (A) is the SI unit of electric current"
                    },
                    {
                        "question": "What happens to kinetic energy when velocity doubles?",
                        "options": ["Doubles", "Triples", "Quadruples", "Remains same"],
                        "correct_answer": 2,
                        "explanation": "KE = ½mv², so when v doubles, KE increases by a factor of 4"
                    }
                ],
                "hard": [
                    {
                        "question": "What is the Schrödinger equation in quantum mechanics?",
                        "options": ["iℏ ∂ψ/∂t = Ĥψ", "E = mc²", "F = ma", "∇²φ = 0"],
                        "correct_answer": 0,
                        "explanation": "The time-dependent Schrödinger equation is iℏ ∂ψ/∂t = Ĥψ, where ψ is the wave function"
                    },
                    {
                        "question": "What is the uncertainty principle?",
                        "options": ["ΔxΔp ≥ ℏ/2", "E = hf", "λ = h/p", "F = qE"],
                        "correct_answer": 0,
                        "explanation": "Heisenberg's uncertainty principle states that ΔxΔp ≥ ℏ/2, where Δx and Δp are uncertainties in position and momentum"
                    }
                ]
            },
            "Chemistry": {
                "easy": [
                    {
                        "question": "What is the chemical formula for water?",
                        "options": ["H₂O", "CO₂", "NaCl", "O₂"],
                        "correct_answer": 0,
                        "explanation": "Water consists of two hydrogen atoms bonded to one oxygen atom"
                    },
                    {
                        "question": "What is the atomic number of carbon?",
                        "options": ["6", "12", "14", "8"],
                        "correct_answer": 0,
                        "explanation": "Carbon has 6 protons, giving it an atomic number of 6"
                    },
                    {
                        "question": "What is the pH of pure water?",
                        "options": ["0", "7", "14", "1"],
                        "correct_answer": 1,
                        "explanation": "Pure water has a neutral pH of 7"
                    }
                ],
                "medium": [
                    {
                        "question": "What type of bond forms between Na and Cl?",
                        "options": ["Covalent", "Ionic", "Metallic", "Hydrogen"],
                        "correct_answer": 1,
                        "explanation": "Sodium and chlorine form an ionic bond due to electron transfer"
                    },
                    {
                        "question": "What is Avogadro's number?",
                        "options": ["6.02 × 10²³", "3.14 × 10⁸", "9.81 × 10²", "1.38 × 10²³"],
                        "correct_answer": 0,
                        "explanation": "Avogadro's number is approximately 6.02 × 10²³ particles per mole"
                    }
                ],
                "hard": [
                    {
                        "question": "What is the molecular orbital theory?",
                        "options": ["Electrons occupy molecular orbitals formed by combining atomic orbitals", "Atoms share electrons equally", "Electrons transfer completely", "Atoms form ionic bonds"],
                        "correct_answer": 0,
                        "explanation": "Molecular orbital theory describes how atomic orbitals combine to form molecular orbitals that can hold electrons"
                    }
                ]
            },
            "Biology": {
                "easy": [
                    {
                        "question": "What is the powerhouse of the cell?",
                        "options": ["Nucleus", "Mitochondria", "Ribosome", "Golgi apparatus"],
                        "correct_answer": 1,
                        "explanation": "Mitochondria produce ATP, the cell's energy currency"
                    },
                    {
                        "question": "What is the process by which plants make food?",
                        "options": ["Respiration", "Photosynthesis", "Digestion", "Fermentation"],
                        "correct_answer": 1,
                        "explanation": "Photosynthesis converts light energy into chemical energy"
                    }
                ],
                "medium": [
                    {
                        "question": "What is DNA replication?",
                        "options": ["Copying DNA", "Breaking down DNA", "Translating DNA", "Transcribing DNA"],
                        "correct_answer": 0,
                        "explanation": "DNA replication is the process of copying DNA to produce identical DNA molecules"
                    }
                ],
                "hard": [
                    {
                        "question": "What is the central dogma of molecular biology?",
                        "options": ["DNA → RNA → Protein", "Protein → RNA → DNA", "RNA → DNA → Protein", "DNA → Protein → RNA"],
                        "correct_answer": 0,
                        "explanation": "The central dogma describes the flow of genetic information: DNA is transcribed to RNA, which is translated to protein"
                    }
                ]
            },
            "Computer Science": {
                "easy": [
                    {
                        "question": "What does CPU stand for?",
                        "options": ["Central Processing Unit", "Computer Personal Unit", "Central Program Unit", "Computer Processing Unit"],
                        "correct_answer": 0,
                        "explanation": "CPU stands for Central Processing Unit, the brain of the computer"
                    },
                    {
                        "question": "What is binary code?",
                        "options": ["Code using 0s and 1s", "Code using letters", "Code using numbers 0-9", "Code using symbols"],
                        "correct_answer": 0,
                        "explanation": "Binary code uses only two digits: 0 and 1, representing off and on states"
                    }
                ],
                "medium": [
                    {
                        "question": "Which data structure follows LIFO principle?",
                        "options": ["Queue", "Stack", "Array", "Linked List"],
                        "correct_answer": 1,
                        "explanation": "Stack follows Last In, First Out (LIFO) principle"
                    },
                    {
                        "question": "What is the time complexity of binary search?",
                        "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
                        "correct_answer": 1,
                        "explanation": "Binary search has O(log n) time complexity as it halves the search space each iteration"
                    }
                ],
                "hard": [
                    {
                        "question": "What is the difference between P and NP problems?",
                        "options": ["P problems can be solved in polynomial time, NP problems can be verified in polynomial time", "P problems are harder than NP", "NP problems are easier than P", "There is no difference"],
                        "correct_answer": 0,
                        "explanation": "P problems can be solved in polynomial time, while NP problems can be verified (but not necessarily solved) in polynomial time"
                    }
                ]
            }
        }
        
        # Get questions for the topic and difficulty
        topic_questions = mock_questions.get(topic, mock_questions["Mathematics"])
        difficulty_questions = topic_questions.get(difficulty, topic_questions.get("medium", []))
        
        # If we don't have enough questions, cycle through them
        questions = []
        for i in range(num_questions):
            if difficulty_questions:
                base_question = difficulty_questions[i % len(difficulty_questions)]
                question = base_question.copy()
                if i >= len(difficulty_questions):
                    question["question"] = f"{question['question']} (Variation {i // len(difficulty_questions) + 1})"
                questions.append(question)
        
        return questions

# Global instance
watsonx_service = WatsonxService()