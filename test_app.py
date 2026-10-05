"""
Automated Integration and Unit Tests for AI Laptop Selection Chatbot
Validates:
1. Database initialization and records
2. Rule Base and Inference Engine scoring
3. Flask endpoints (/chat, /recommend, /compare, /reset, /api/laptops)
4. NLP requirement extraction and compound sentence parsing
5. Explainable AI outputs and comparison logic
"""

import unittest
import json
from app import app
from database import init_db, get_all_laptops
from expert_system import InferenceEngine
from chatbot import NLPExtractor, ChatbotSession


class TestLaptopChatbot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = app.test_client()

    def test_database_records(self):
        """Verify knowledge base contains >= 15 sample laptops."""
        laptops = get_all_laptops()
        self.assertGreaterEqual(len(laptops), 15)
        for lap in laptops:
            self.assertIn("name", lap)
            self.assertIn("price", lap)
            self.assertIn("ram", lap)
            self.assertIn("gpu", lap)
            self.assertIn("cpu_score", lap)
            self.assertIn("primary_usage", lap)

    def test_nlp_extraction(self):
        """Verify natural language understanding on various input formats."""
        self.assertEqual(NLPExtractor.extract_budget("70k"), 70000)
        self.assertEqual(NLPExtractor.extract_budget("₹65,000"), 65000)
        self.assertEqual(NLPExtractor.extract_budget("my budget is 80 thousand"), 80000)
        self.assertEqual(NLPExtractor.extract_usage("coding"), "Programming")
        self.assertEqual(NLPExtractor.extract_usage("I want to play valorant and games"), "Gaming")
        self.assertEqual(NLPExtractor.extract_ram("16 gigs"), 16)
        self.assertEqual(NLPExtractor.extract_ram("32GB"), 32)
        self.assertEqual(NLPExtractor.extract_storage("1tb"), 1024)

    def test_inference_engine_scoring(self):
        """Verify forward chaining and scoring calculation."""
        ie = InferenceEngine()
        reqs = {
            "budget": 75000,
            "usage": "Programming",
            "ram": 16,
            "storage": 512,
            "gpu": "RTX 4050",
            "processor": "AMD",
            "battery": "Average",
            "portability": "Moderate"
        }
        res = ie.recommend(reqs, top_n=3)
        top = res["top_matches"]
        self.assertGreater(len(top), 0)
        best = top[0]
        self.assertGreaterEqual(best["total_score"], 80)
        self.assertTrue(len(best["matched_reasons"]) > 0)
        self.assertIn("budget", best["sub_scores"])

    def test_flask_endpoints(self):
        """Verify REST API routes return correct status codes and JSON."""
        # Test index page
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)

        # Test catalog API
        res = self.client.get("/api/laptops")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("laptops", data)
        self.assertGreaterEqual(data["count"], 15)

        # Test /reset
        res = self.client.post("/reset")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("reply", data)
        self.assertIn("options", data)

        # Test /chat step-by-step
        res = self.client.post("/chat", json={"message": "70k"})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("reply", data)

        # Test /recommend direct
        res = self.client.post("/recommend", json={"budget": 80000, "usage": "Gaming"})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("top_matches", data)

        # Test /compare
        res = self.client.post("/compare", json={"id1": 1, "id2": 2})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("features", data)
        self.assertIn("conclusion", data)

    def test_full_conversational_flow_and_followups(self):
        """Simulate an entire user session from greeting to follow-ups."""
        session = ChatbotSession()
        res = session.reset()
        self.assertEqual(res["status"], "in_progress")
        self.assertIn("budget", res["reply"].lower())

        # Q1: Budget
        res = session.handle_message("70k")
        self.assertIn("use", res["reply"].lower())

        # Q2: Usage
        res = session.handle_message("Programming")
        self.assertIn("ram", res["reply"].lower())

        # Q3: RAM
        res = session.handle_message("16 GB")
        self.assertIn("storage", res["reply"].lower())

        # Q4: Storage
        res = session.handle_message("512 GB")
        self.assertIn("graphics", res["reply"].lower())

        # Q5: GPU
        res = session.handle_message("RTX 4050")
        self.assertIn("processor", res["reply"].lower())

        # Q6: Processor
        res = session.handle_message("No preference")
        self.assertIn("battery", res["reply"].lower())

        # Q7: Battery
        res = session.handle_message("Average")
        self.assertIn("lightweight", res["reply"].lower())

        # Q8: Portability -> Completed recommendation!
        res = session.handle_message("Moderate")
        self.assertEqual(res["status"], "completed")
        self.assertIn("Best Match", res["reply"])
        self.assertIn("recommendation", res)
        best_name = res["recommendation"]["best"]["laptop"]["name"]

        # Follow-up: Why this laptop?
        res_why = session.handle_message("why this laptop?")
        self.assertEqual(res_why["status"], "follow_up")
        self.assertIn("Rule Analysis", res_why["reply"])

        # Follow-up: Gaming
        res_game = session.handle_message("is it good for gaming?")
        self.assertEqual(res_game["status"], "follow_up")
        self.assertIn("Gaming Verdict", res_game["reply"])

        # Follow-up: Cheaper options
        res_cheap = session.handle_message("show cheaper options")
        self.assertEqual(res_cheap["status"], "follow_up")
        self.assertIn("Cheaper Alternatives", res_cheap["reply"])

        # Follow-up: Compare top 2
        res_cmp = session.handle_message("compare top 2 laptops")
        self.assertEqual(res_cmp["status"], "comparison")
        self.assertIn("Head-to-Head Comparison", res_cmp["reply"])

        # Reset command
        res_reset = session.handle_message("restart")
        self.assertEqual(res_reset["status"], "in_progress")
        self.assertIn("maximum budget", res_reset["reply"])

    def test_error_handling_and_recovery(self):
        """Ensure chatbot never crashes on garbage or edge-case input."""
        session = ChatbotSession()
        session.reset()

        # Empty string
        res = session.handle_message("")
        self.assertEqual(res["status"], "waiting")

        # Invalid budget string
        res = session.handle_message("random text without numbers")
        self.assertEqual(res["status"], "error")
        self.assertIn("couldn't quite understand", res["reply"])

        # Very low budget (< 30k)
        res = session.handle_message("15000")
        self.assertEqual(res["status"], "error")
        self.assertIn("38,990", res["reply"])

        # Valid recovery
        res = session.handle_message("50000")
        self.assertEqual(res["status"], "in_progress")
        self.assertIn("use", res["reply"].lower())


if __name__ == "__main__":
    unittest.main()
