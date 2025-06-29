import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "edututorai")
        
        if not self.api_key:
            logger.warning("Pinecone API key not found, using mock storage")
            self.client = None
            self.index = None
            # Enhanced mock storage for development
            self.mock_storage = {
                "user_profiles": {},
                "quiz_history": {},
                "embeddings": {},
                "learning_patterns": {},
                "adaptive_data": {}
            }
        else:
            try:
                import pinecone
                from pinecone import Pinecone
                
                # Initialize Pinecone with new API
                pc = Pinecone(api_key=self.api_key)
                self.index = pc.Index(self.index_name)
                logger.info("✅ Pinecone initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone: {e}")
                self.index = None
                self.mock_storage = {
                    "user_profiles": {},
                    "quiz_history": {},
                    "embeddings": {},
                    "learning_patterns": {},
                    "adaptive_data": {}
                }

    def store_user_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Store user profile with embeddings"""
        try:
            if self.index:
                # Generate embedding for user profile
                embedding = self._generate_profile_embedding(profile_data)
                
                # Upsert to Pinecone
                self.index.upsert(
                    vectors=[(user_id, embedding, profile_data)]
                )
                return True
            else:
                # Mock storage
                self.mock_storage["user_profiles"][user_id] = profile_data
                return True
                
        except Exception as e:
            logger.error(f"Error storing user profile: {e}")
            return False

    def store_quiz_attempt(self, user_id: str, quiz_data: Dict) -> bool:
        """Store quiz attempt data with enhanced analytics"""
        try:
            attempt_id = f"{user_id}_{datetime.now().timestamp()}"
            
            if self.index:
                # Generate embedding for quiz content
                embedding = self._generate_quiz_embedding(quiz_data)
                
                # Upsert to Pinecone
                self.index.upsert(
                    vectors=[(attempt_id, embedding, quiz_data)]
                )
                return True
            else:
                # Enhanced mock storage
                if user_id not in self.mock_storage["quiz_history"]:
                    self.mock_storage["quiz_history"][user_id] = []
                self.mock_storage["quiz_history"][user_id].append(quiz_data)
                
                # Update learning patterns
                self._update_learning_patterns(user_id, quiz_data)
                return True
                
        except Exception as e:
            logger.error(f"Error storing quiz attempt: {e}")
            return False

    def _update_learning_patterns(self, user_id: str, quiz_data: Dict):
        """Update learning patterns for adaptive recommendations"""
        if user_id not in self.mock_storage["learning_patterns"]:
            self.mock_storage["learning_patterns"][user_id] = {
                "topics": {},
                "difficulties": {},
                "performance_trend": [],
                "learning_velocity": 0,
                "preferred_topics": [],
                "weak_areas": []
            }
        
        patterns = self.mock_storage["learning_patterns"][user_id]
        topic = quiz_data.get("topic", "Unknown")
        difficulty = quiz_data.get("difficulty", "medium")
        score = quiz_data.get("score", 0)
        
        # Update topic performance
        if topic not in patterns["topics"]:
            patterns["topics"][topic] = {"scores": [], "attempts": 0}
        patterns["topics"][topic]["scores"].append(score)
        patterns["topics"][topic]["attempts"] += 1
        
        # Update difficulty performance
        if difficulty not in patterns["difficulties"]:
            patterns["difficulties"][difficulty] = {"scores": [], "attempts": 0}
        patterns["difficulties"][difficulty]["scores"].append(score)
        patterns["difficulties"][difficulty]["attempts"] += 1
        
        # Update performance trend
        patterns["performance_trend"].append({
            "score": score,
            "timestamp": quiz_data.get("timestamp"),
            "topic": topic
        })
        
        # Keep only last 20 attempts for trend analysis
        if len(patterns["performance_trend"]) > 20:
            patterns["performance_trend"] = patterns["performance_trend"][-20:]
        
        # Update preferred topics and weak areas
        self._analyze_preferences(user_id)

    def _analyze_preferences(self, user_id: str):
        """Analyze user preferences and weak areas"""
        patterns = self.mock_storage["learning_patterns"].get(user_id, {})
        topics = patterns.get("topics", {})
        
        # Calculate topic averages
        topic_averages = {}
        for topic, data in topics.items():
            if data["scores"]:
                topic_averages[topic] = sum(data["scores"]) / len(data["scores"])
        
        # Identify preferred topics (score >= 75)
        preferred = [topic for topic, avg in topic_averages.items() if avg >= 75]
        
        # Identify weak areas (score < 60)
        weak = [topic for topic, avg in topic_averages.items() if avg < 60]
        
        patterns["preferred_topics"] = preferred
        patterns["weak_areas"] = weak

    def get_user_quiz_history(self, user_id: str) -> List[Dict]:
        """Get comprehensive quiz history for a user"""
        try:
            if self.index:
                # Query Pinecone for user's quiz history
                # This would require more complex querying logic
                return []
            else:
                # Enhanced mock storage with analytics
                history = self.mock_storage["quiz_history"].get(user_id, [])
                patterns = self.mock_storage["learning_patterns"].get(user_id, {})
                
                return {
                    "attempts": history,
                    "patterns": patterns,
                    "total_attempts": len(history),
                    "topics_covered": len(patterns.get("topics", {})),
                    "average_score": self._calculate_average_score(history)
                }
                
        except Exception as e:
            logger.error(f"Error getting quiz history: {e}")
            return []

    def _calculate_average_score(self, history: List[Dict]) -> float:
        """Calculate average score from history"""
        if not history:
            return 0
        scores = [attempt.get("score", 0) for attempt in history]
        return sum(scores) / len(scores)

    def get_similar_users(self, user_id: str, top_k: int = 5) -> List[Dict]:
        """Find users with similar learning patterns"""
        try:
            if self.index:
                # Get user profile
                user_profile = self._get_user_profile(user_id)
                if not user_profile:
                    return []
                
                # Generate embedding and query for similar users
                embedding = self._generate_profile_embedding(user_profile)
                results = self.index.query(
                    vector=embedding,
                    top_k=top_k,
                    include_metadata=True
                )
                
                return [match.metadata for match in results.matches if match.id != user_id]
            else:
                # Enhanced mock similar users with learning patterns
                user_patterns = self.mock_storage["learning_patterns"].get(user_id, {})
                user_topics = set(user_patterns.get("topics", {}).keys())
                
                similar_users = []
                for other_user_id, other_patterns in self.mock_storage["learning_patterns"].items():
                    if other_user_id != user_id:
                        other_topics = set(other_patterns.get("topics", {}).keys())
                        
                        # Calculate similarity based on common topics
                        common_topics = user_topics.intersection(other_topics)
                        similarity = len(common_topics) / max(len(user_topics), len(other_topics), 1)
                        
                        if similarity > 0.3:  # Threshold for similarity
                            similar_users.append({
                                "user_id": other_user_id,
                                "similarity_score": similarity,
                                "common_topics": list(common_topics)
                            })
                
                # Sort by similarity and return top_k
                similar_users.sort(key=lambda x: x["similarity_score"], reverse=True)
                return similar_users[:top_k]
                
        except Exception as e:
            logger.error(f"Error finding similar users: {e}")
            return []

    def get_adaptive_recommendations(self, user_id: str) -> Dict:
        """Get comprehensive adaptive learning recommendations"""
        try:
            quiz_history = self.mock_storage["quiz_history"].get(user_id, [])
            patterns = self.mock_storage["learning_patterns"].get(user_id, {})
            
            if not quiz_history:
                return {
                    "recommended_topics": ["Mathematics", "Physics", "Chemistry"],
                    "recommended_difficulty": "medium",
                    "focus_areas": [],
                    "learning_path": [],
                    "next_steps": "Start with a diagnostic test to assess your current level."
                }
            
            # Analyze performance patterns
            topic_performance = patterns.get("topics", {})
            difficulty_performance = patterns.get("difficulties", {})
            performance_trend = patterns.get("performance_trend", [])
            
            # Calculate overall performance metrics
            recent_scores = [attempt["score"] for attempt in performance_trend[-5:]]
            overall_avg = sum(recent_scores) / len(recent_scores) if recent_scores else 50
            
            # Determine recommended difficulty
            if overall_avg >= 85:
                recommended_difficulty = "hard"
            elif overall_avg >= 70:
                recommended_difficulty = "medium"
            else:
                recommended_difficulty = "easy"
            
            # Get weak areas and focus topics
            weak_areas = patterns.get("weak_areas", [])
            preferred_topics = patterns.get("preferred_topics", [])
            
            # Generate learning path
            learning_path = self._generate_learning_path(topic_performance, weak_areas, preferred_topics)
            
            # Generate next steps
            next_steps = self._generate_next_steps(overall_avg, weak_areas, performance_trend)
            
            return {
                "recommended_topics": weak_areas[:3] if weak_areas else list(topic_performance.keys())[:3],
                "recommended_difficulty": recommended_difficulty,
                "focus_areas": weak_areas,
                "preferred_topics": preferred_topics,
                "topic_performance": {
                    topic: sum(data["scores"]) / len(data["scores"]) 
                    for topic, data in topic_performance.items() 
                    if data["scores"]
                },
                "learning_path": learning_path,
                "next_steps": next_steps,
                "performance_trend": "improving" if self._is_improving(performance_trend) else "stable",
                "overall_score": overall_avg
            }
            
        except Exception as e:
            logger.error(f"Error getting adaptive recommendations: {e}")
            return {
                "recommended_topics": ["Mathematics"],
                "recommended_difficulty": "medium",
                "focus_areas": [],
                "learning_path": [],
                "next_steps": "Continue practicing to improve your skills."
            }

    def _generate_learning_path(self, topic_performance: Dict, weak_areas: List[str], preferred_topics: List[str]) -> List[Dict]:
        """Generate personalized learning path"""
        path = []
        
        # Start with weak areas
        for topic in weak_areas[:2]:
            path.append({
                "topic": topic,
                "priority": "high",
                "reason": "Needs improvement",
                "suggested_difficulty": "easy"
            })
        
        # Add preferred topics for reinforcement
        for topic in preferred_topics[:2]:
            if topic not in weak_areas:
                path.append({
                    "topic": topic,
                    "priority": "medium",
                    "reason": "Strengthen existing knowledge",
                    "suggested_difficulty": "medium"
                })
        
        # Add new topics for exploration
        all_topics = ["Mathematics", "Physics", "Chemistry", "Biology", "Computer Science"]
        covered_topics = set(topic_performance.keys())
        new_topics = [t for t in all_topics if t not in covered_topics]
        
        for topic in new_topics[:1]:
            path.append({
                "topic": topic,
                "priority": "low",
                "reason": "Explore new subject",
                "suggested_difficulty": "easy"
            })
        
        return path

    def _generate_next_steps(self, overall_avg: float, weak_areas: List[str], performance_trend: List[Dict]) -> str:
        """Generate personalized next steps"""
        if overall_avg >= 90:
            return "Excellent progress! Consider exploring advanced topics or helping other students."
        elif overall_avg >= 75:
            if weak_areas:
                return f"Good work! Focus on improving in {', '.join(weak_areas[:2])} to reach the next level."
            else:
                return "Great job! Try increasing the difficulty level for more challenge."
        elif overall_avg >= 60:
            return f"You're making progress. Concentrate on {', '.join(weak_areas[:2])} and practice regularly."
        else:
            return "Keep practicing! Start with easier questions and gradually increase difficulty."

    def _is_improving(self, performance_trend: List[Dict]) -> bool:
        """Check if user performance is improving"""
        if len(performance_trend) < 3:
            return False
        
        recent_scores = [attempt["score"] for attempt in performance_trend[-3:]]
        earlier_scores = [attempt["score"] for attempt in performance_trend[-6:-3]] if len(performance_trend) >= 6 else []
        
        if not earlier_scores:
            return False
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        earlier_avg = sum(earlier_scores) / len(earlier_scores)
        
        return recent_avg > earlier_avg

    def get_class_analytics(self, class_id: str) -> Dict:
        """Get analytics for a specific class"""
        try:
            # Mock class analytics
            return {
                "class_id": class_id,
                "total_students": 25,
                "active_students": 20,
                "average_score": 78,
                "completion_rate": 85,
                "top_performers": [
                    {"name": "Alice Johnson", "score": 95},
                    {"name": "Bob Smith", "score": 92},
                    {"name": "Carol Davis", "score": 89}
                ],
                "struggling_students": [
                    {"name": "David Wilson", "score": 45},
                    {"name": "Emma Brown", "score": 52}
                ],
                "topic_performance": {
                    "Mathematics": 82,
                    "Physics": 75,
                    "Chemistry": 79
                }
            }
        except Exception as e:
            logger.error(f"Error getting class analytics: {e}")
            return {}

    def _generate_profile_embedding(self, profile_data: Dict) -> List[float]:
        """Generate embedding for user profile"""
        # In a real implementation, this would use a proper embedding model
        # For now, return a mock embedding based on profile characteristics
        
        # Create a simple embedding based on learning preferences
        embedding = [0.0] * 384  # Mock 384-dimensional embedding
        
        # Encode some basic features
        if "preferred_topics" in profile_data:
            for i, topic in enumerate(profile_data["preferred_topics"][:5]):
                embedding[i] = hash(topic) % 100 / 100.0
        
        if "average_score" in profile_data:
            embedding[10] = profile_data["average_score"] / 100.0
        
        return embedding

    def _generate_quiz_embedding(self, quiz_data: Dict) -> List[float]:
        """Generate embedding for quiz data"""
        # Mock embedding generation
        embedding = [0.0] * 384
        
        # Encode quiz features
        if "topic" in quiz_data:
            embedding[0] = hash(quiz_data["topic"]) % 100 / 100.0
        
        if "difficulty" in quiz_data:
            difficulty_map = {"easy": 0.3, "medium": 0.6, "hard": 0.9}
            embedding[1] = difficulty_map.get(quiz_data["difficulty"], 0.5)
        
        if "score" in quiz_data:
            embedding[2] = quiz_data["score"] / 100.0
        
        return embedding

    def _get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile from storage"""
        if self.index:
            # Query Pinecone for user profile
            return None  # Simplified for mock
        else:
            return self.mock_storage["user_profiles"].get(user_id)

# Global instance
pinecone_service = PineconeService()