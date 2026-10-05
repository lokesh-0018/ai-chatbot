"""
Chatbot Logic and Natural Language Understanding Module
Handles conversational state, requirement extraction, follow-up queries, and commands.
"""

import re
from expert_system import InferenceEngine

# Question Flow Definitions
QUESTIONS = [
    {
        "id": "budget",
        "question": "What is your maximum budget?",
        "options": ["₹40,000", "₹50,000", "₹60,000", "₹70,000", "₹80,000", "₹1,00,000+"],
        "helper": "Tip: You can type '70k', '₹65,000', or 'under 80000'."
    },
    {
        "id": "usage",
        "question": "What will you mainly use the laptop for?",
        "options": [
            "💻 Programming",
            "🎓 Student / Education",
            "🎮 Gaming",
            "🎬 Video Editing",
            "🎨 Graphic Design",
            "🤖 AI / Machine Learning",
            "💼 Office Work",
            "🌐 General Use"
        ],
        "helper": "You can select an option or type in your own words (e.g., 'coding and Docker')."
    },
    {
        "id": "ram",
        "question": "How much RAM do you need?",
        "options": ["8 GB", "16 GB", "32 GB", "64 GB"],
        "helper": "16 GB is recommended for programming and modern gaming."
    },
    {
        "id": "storage",
        "question": "How much storage do you prefer?",
        "options": ["256 GB SSD", "512 GB SSD", "1 TB SSD", "2 TB SSD"],
        "helper": "512 GB or 1 TB NVMe SSD is best for fast app loading."
    },
    {
        "id": "gpu",
        "question": "Do you need a dedicated graphics card?",
        "options": [
            "No GPU / Integrated",
            "RTX 3050",
            "RTX 4050",
            "RTX 4060",
            "RTX 4070+",
            "No preference"
        ],
        "helper": "Dedicated GPUs (NVIDIA RTX) are essential for gaming, 3D render, and AI."
    },
    {
        "id": "processor",
        "question": "Do you have a processor preference?",
        "options": ["Intel", "AMD", "No preference"],
        "helper": "Both Intel Core and AMD Ryzen offer excellent multi-core performance."
    },
    {
        "id": "battery",
        "question": "How important is battery life?",
        "options": ["Basic (4-5 hrs)", "Average (6-7 hrs)", "High (8+ hrs)"],
        "helper": "High battery life is ideal for campus and travel."
    },
    {
        "id": "portability",
        "question": "Do you need a lightweight laptop?",
        "options": ["Very Important (< 1.5kg)", "Moderate (1.5 - 2.2kg)", "Not Important (> 2kg)"],
        "helper": "Ultralight models are easiest to carry; gaming rigs are usually heavier."
    }
]


class NLPExtractor:
    """Extracts specifications, numbers, preferences, and intents from natural language."""

    @staticmethod
    def extract_budget(text):
        clean = text.lower().replace(",", "").replace("₹", "").replace("rs.", "").replace("inr", "")

        # Check for patterns like "70k", "75.5k"
        k_match = re.search(r"(\d+(?:\.\d+)?)\s*k\b", clean)
        if k_match:
            return int(float(k_match.group(1)) * 1000)

        # Check for "70 thousand", "1 lakh"
        thousand_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:thousand|k)", clean)
        if thousand_match:
            return int(float(thousand_match.group(1)) * 1000)

        lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lac)", clean)
        if lakh_match:
            return int(float(lakh_match.group(1)) * 100000)

        # Check for explicit numbers like 70000, 100000
        num_match = re.search(r"\b(\d{4,7})\b", clean)
        if num_match:
            val = int(num_match.group(1))
            if 15000 <= val <= 500000:
                return val

        # Special phrase: "1,00,000+" or "100000+"
        if "100000" in clean or "1 lakh" in clean or "1lakh" in clean or "100k" in clean:
            return 120000

        return None

    @staticmethod
    def extract_usage(text):
        t = text.lower()
        if re.search(r"\b(1|prog\w*|cod\w*|dev\w*|soft\w*|java|python|c\+\+|flutter|backend|frontend)\b", t):
            return "Programming"
        if re.search(r"\b(2|stud\w*|school|college|educat\w*|academic|notes|class|lecture)\b", t):
            return "Student / Education"
        if re.search(r"\b(3|gam\w*|gta|valorant|fps|cyberpunk|steam|esports)\b", t):
            return "Gaming"
        if re.search(r"\b(4|video\w*|edit\w*|render\w*|premiere|davinci|after effects|youtube)\b", t):
            return "Video Editing"
        if re.search(r"\b(5|graph\w*|design\w*|photoshop|illustrator|ui|ux|figma|3d|blender|art)\b", t):
            return "Graphic Design"
        if re.search(r"\b(6|ai\b|ml\b|machine\s*learn\w*|deep\s*learn\w*|data\s*sci\w*|neural|pytorch|tensorflow|llm|nlp)\b", t):
            return "AI / Machine Learning"
        if re.search(r"\b(7|office\w*|excel|ppt|powerpoint|word|business|accounting|work\b)\b", t):
            return "Office Work"
        if re.search(r"\b(8|general\w*|brows\w*|netflix|movies|daily|casual)\b", t):
            return "General Use"
        return None

    @staticmethod
    def extract_ram(text):
        t = text.lower().replace("gigabytes", "gb").replace("gigs", "gb").replace("gig", "gb")
        if re.search(r"\b64\s*(gb)?\b", t):
            return 64
        if re.search(r"\b32\s*(gb)?\b", t):
            return 32
        if re.search(r"\b16\s*(gb)?\b", t):
            return 16
        if re.search(r"\b8\s*(gb)?\b", t):
            return 8
        if "no preference" in t or "any" in t:
            return 16
        return None

    @staticmethod
    def extract_storage(text):
        t = text.lower()
        if re.search(r"\b2\s*(tb|tb ssd)\b", t):
            return 2048
        if re.search(r"\b1\s*(tb|tb ssd|tera)\b", t) or "1024" in t:
            return 1024
        if re.search(r"\b512\s*(gb|gb ssd)?\b", t):
            return 512
        if re.search(r"\b256\s*(gb|gb ssd)?\b", t):
            return 256
        if "no preference" in t or "any" in t:
            return 512
        return None

    @staticmethod
    def extract_gpu(text):
        t = text.lower()
        if "4070" in t:
            return "RTX 4070+"
        if "4060" in t:
            return "RTX 4060"
        if "4050" in t:
            return "RTX 4050"
        if "3050" in t:
            return "RTX 3050"
        if "no gpu" in t or "integrated" in t or "iris" in t or "radeon" in t or "none" in t or "don't need" in t:
            return "No GPU / Integrated"
        if "no preference" in t or "any" in t or "whatever" in t:
            return "No preference"
        if "dedicated" in t or "nvidia" in t or "rtx" in t or "gpu" in t:
            return "RTX 4050"
        return None

    @staticmethod
    def extract_processor(text):
        t = text.lower()
        if "intel" in t or "core i" in t or "i5" in t or "i7" in t or "i9" in t:
            return "Intel"
        if "amd" in t or "ryzen" in t:
            return "AMD"
        if "apple" in t or "mac" in t or "m2" in t or "m3" in t:
            return "Apple"
        if "no preference" in t or "any" in t or "either" in t:
            return "No preference"
        return None

    @staticmethod
    def extract_battery(text):
        t = text.lower()
        if "high" in t or "8+" in t or "8 hrs" in t or "long" in t or "all day" in t:
            return "High"
        if "average" in t or "6-7" in t or "6" in t or "7" in t or "normal" in t:
            return "Average"
        if "basic" in t or "4-5" in t or "low" in t or "plugged in" in t:
            return "Basic"
        if "no preference" in t or "any" in t:
            return "Average"
        return None

    @staticmethod
    def extract_portability(text):
        t = text.lower()
        if "very" in t or "light" in t or "ultrabook" in t or "slim" in t or "portable" in t:
            return "Very Important"
        if "moderate" in t or "medium" in t or "balanced" in t:
            return "Moderate"
        if "not" in t or "heavy" in t or "desk" in t or "gaming" in t:
            return "Not Important"
        if "no preference" in t or "any" in t:
            return "Moderate"
        return None

    @classmethod
    def extract_multi(cls, text):
        """Extracts any known requirement present in a compound sentence."""
        res = {}
        b = cls.extract_budget(text)
        if b:
            res["budget"] = b
        u = cls.extract_usage(text)
        if u:
            res["usage"] = u
        r = cls.extract_ram(text)
        if r:
            res["ram"] = r
        s = cls.extract_storage(text)
        if s:
            res["storage"] = s
        g = cls.extract_gpu(text)
        if g:
            res["gpu"] = g
        p = cls.extract_processor(text)
        if p:
            res["processor"] = p
        return res


class ChatbotSession:
    """Manages conversational state, interactive turns, and expert queries for a user."""

    def __init__(self, session_id="default"):
        self.session_id = session_id
        self.inference_engine = InferenceEngine()
        self.reset()

    def reset(self):
        """Resets the conversation to the beginning."""
        self.current_step = 0
        self.requirements = {
            "budget": None,
            "usage": None,
            "ram": None,
            "storage": None,
            "gpu": None,
            "processor": None,
            "battery": None,
            "portability": None
        }
        self.history = []
        self.last_recommendation = None
        self.is_completed = False

        greeting = (
            "Hello! 👋 I'm your **Laptop Selection Expert**.\n\n"
            "I will help you find the absolute best laptop based on your budget, "
            "usage needs, performance expectations, and portability preferences."
        )
        first_q = QUESTIONS[0]
        return {
            "reply": f"{greeting}\n\n**{first_q['question']}**",
            "options": first_q["options"],
            "helper": first_q["helper"],
            "step": self.current_step,
            "status": "in_progress"
        }

    def handle_message(self, message_text):
        """Processes an incoming user message and returns an expert response."""
        text = (message_text or "").strip()
        if not text:
            return {
                "reply": "Please send a message or select one of the suggested options below.",
                "options": self._get_current_options(),
                "status": "waiting"
            }

        lower = text.lower()

        # Handle global commands
        if lower in ["restart", "start again", "reset", "clear", "new"]:
            return self.reset()

        if lower in ["help", "commands"]:
            return {
                "reply": (
                    "💡 **Available Commands:**\n"
                    "- `restart` or `start again`: Begin a new laptop search.\n"
                    "- `why this laptop?`: Explain the AI reasoning for the top recommendation.\n"
                    "- `is it good for gaming?`: Check gaming capabilities.\n"
                    "- `show cheaper options`: Find more affordable laptops.\n"
                    "- `i want more ram`: Filter for 32GB+ RAM models.\n"
                    "- `show alternatives`: View Alternative 1 and Alternative 2.\n"
                    "- `compare laptops`: See a side-by-side comparison table of top 2 laptops.\n"
                    "- `best gaming laptop`: See the top gaming machine in knowledge base."
                ),
                "options": ["show alternatives", "compare laptops", "show cheaper options", "restart"],
                "status": "info"
            }

        # Handle compound requirements mentioned upfront
        multi = NLPExtractor.extract_multi(text)
        if len(multi) > 1 and not self.is_completed:
            for k, v in multi.items():
                self.requirements[k] = v
            # Advance step to the first unanswered requirement
            self._advance_to_next_unfilled()
            if self.is_completed:
                return self._generate_recommendation_response(
                    prefix="Great! I extracted your requirements: " +
                           ", ".join([f"{k}: {v}" for k, v in multi.items()]) + ".\n\n"
                )
            else:
                next_q = QUESTIONS[self.current_step]
                return {
                    "reply": (
                        f"Great! I noted: " +
                        ", ".join([f"{k.capitalize()}: {v}" for k, v in multi.items()]) + ".\n\n"
                        f"**{next_q['question']}**"
                    ),
                    "options": next_q["options"],
                    "helper": next_q["helper"],
                    "step": self.current_step,
                    "status": "in_progress"
                }

        # If already completed recommendation, handle follow-up queries & commands
        if self.is_completed:
            return self._handle_follow_up(text)

        # Standard step-by-step questioning
        return self._process_step(text)

    def _get_current_options(self):
        if self.current_step < len(QUESTIONS):
            return QUESTIONS[self.current_step]["options"]
        return ["show alternatives", "compare laptops", "show cheaper options", "restart"]

    def _advance_to_next_unfilled(self):
        while self.current_step < len(QUESTIONS):
            q_id = QUESTIONS[self.current_step]["id"]
            if self.requirements.get(q_id) is None:
                break
            self.current_step += 1
        if self.current_step >= len(QUESTIONS):
            self.is_completed = True

    def _process_step(self, text):
        curr_q = QUESTIONS[self.current_step]
        q_id = curr_q["id"]

        # Parse based on current question id
        if q_id == "budget":
            val = NLPExtractor.extract_budget(text)
            if not val:
                return {
                    "reply": (
                        "I couldn't quite understand that budget. 🤔\n"
                        "Please enter your budget in Rupees (e.g., **₹60,000**, **70k**, or **75000**), "
                        "or pick one of the options below:"
                    ),
                    "options": curr_q["options"],
                    "helper": curr_q["helper"],
                    "status": "error"
                }
            if val < 30000:
                return {
                    "reply": (
                        f"You entered ₹{val:,}. Laptops in our current knowledge base start at **₹38,990** "
                        f"(Lenovo IdeaPad Slim 3).\n\n"
                        f"Would you like to set your budget to **₹40,000** to explore the most affordable options?"
                    ),
                    "options": ["₹40,000", "₹50,000", "₹60,000"],
                    "helper": "Select ₹40,000 to proceed.",
                    "status": "error"
                }
            self.requirements["budget"] = val

        elif q_id == "usage":
            val = NLPExtractor.extract_usage(text)
            if not val:
                return {
                    "reply": (
                        "Please choose a primary usage from the list or type your intent "
                        "(e.g., Programming, Gaming, Student, Video Editing, AI/ML):"
                    ),
                    "options": curr_q["options"],
                    "helper": curr_q["helper"],
                    "status": "error"
                }
            self.requirements["usage"] = val

        elif q_id == "ram":
            val = NLPExtractor.extract_ram(text)
            if val is None:
                return {
                    "reply": "Please select how much RAM you prefer (8 GB, 16 GB, 32 GB, or 64 GB):",
                    "options": curr_q["options"],
                    "helper": curr_q["helper"],
                    "status": "error"
                }
            self.requirements["ram"] = val

        elif q_id == "storage":
            val = NLPExtractor.extract_storage(text)
            if val is None:
                return {
                    "reply": "Please specify your storage preference (256 GB, 512 GB, 1 TB, or 2 TB):",
                    "options": curr_q["options"],
                    "helper": curr_q["helper"],
                    "status": "error"
                }
            self.requirements["storage"] = val

        elif q_id == "gpu":
            val = NLPExtractor.extract_gpu(text)
            if val is None:
                val = "No preference"
            self.requirements["gpu"] = val

        elif q_id == "processor":
            val = NLPExtractor.extract_processor(text)
            if val is None:
                val = "No preference"
            self.requirements["processor"] = val

        elif q_id == "battery":
            val = NLPExtractor.extract_battery(text)
            if val is None:
                val = "Average"
            self.requirements["battery"] = val

        elif q_id == "portability":
            val = NLPExtractor.extract_portability(text)
            if val is None:
                val = "Moderate"
            self.requirements["portability"] = val

        # Advance to next question or complete
        self.current_step += 1
        self._advance_to_next_unfilled()

        if self.is_completed:
            return self._generate_recommendation_response()

        next_q = QUESTIONS[self.current_step]
        return {
            "reply": f"Got it! 👍\n\n**{next_q['question']}**",
            "options": next_q["options"],
            "helper": next_q["helper"],
            "step": self.current_step,
            "status": "in_progress"
        }

    def _generate_recommendation_response(self, prefix=""):
        """Runs the expert system inference engine and builds the full recommendation card."""
        self.is_completed = True
        rec_data = self.inference_engine.recommend(self.requirements, top_n=3)
        self.last_recommendation = rec_data

        top_matches = rec_data["top_matches"]
        if not top_matches:
            return {
                "reply": "No matching laptops were found for these exact constraints. Try increasing your budget or relaxing constraints.",
                "options": ["restart"],
                "status": "no_match"
            }

        best = top_matches[0]
        laptop = best["laptop"]
        score = best["total_score"]

        # Build Explainable AI summary
        explanation_summary = (
            f"I recommend the **{laptop['name']}** because it matches your ₹{self.requirements.get('budget', 0):,} budget, "
            f"comes with {laptop['ram']} GB RAM, provides a high-performing {laptop['processor']} processor "
            f"for {self.requirements.get('usage', 'general computing')}, and features {laptop['gpu']}."
        )

        response_text = (
            f"{prefix}Thanks! I have analyzed your requirements using our **Rule-Based Inference Engine**. 🔍\n\n"
            f"### 🏆 Best Match: **{laptop['name']}**\n"
            f"- **Compatibility Score:** `{score}/100`\n"
            f"- **Price:** ₹{laptop['price']:,}\n"
            f"- **Processor:** {laptop['processor']}\n"
            f"- **RAM:** {laptop['ram']} GB DDR\n"
            f"- **Storage:** {laptop['storage']} GB SSD\n"
            f"- **Graphics (GPU):** {laptop['gpu']}\n"
            f"- **Display:** {laptop['display']}\" ({laptop['refresh_rate']}Hz)\n"
            f"- **Battery Life:** {laptop['battery']} hours\n"
            f"- **Weight:** {laptop['weight']} kg\n\n"
            f"**💡 Why I Selected This (Explainable AI):**\n"
            f"{explanation_summary}\n\n"
            f"**Matched Requirements:**\n" +
            "\n".join([f"✓ {m}" for m in best["matched_reasons"][:5]])
        )

        if best["limitations"]:
            response_text += "\n\n**Keep In Mind (Limitations):**\n" + "\n".join([f"⚠ {l}" for l in best["limitations"][:3]])

        response_text += (
            "\n\n---\n"
            "💬 You can ask me follow-up questions like: "
            "*'Why did you choose this laptop?'*, *'Is it good for gaming?'*, *'Show cheaper options'*, "
            "*'Compare top 2 laptops'*, or *'Show alternatives'*."
        )

        return {
            "reply": response_text,
            "options": ["Show alternatives", "Compare top 2 laptops", "Why this laptop?", "Show cheaper options", "Restart"],
            "recommendation": {
                "best": best,
                "alternatives": top_matches[1:],
                "comparative_notes": rec_data["comparative_notes"]
            },
            "status": "completed"
        }

    def _handle_follow_up(self, text):
        """Handles conversational follow-up questions after the recommendation has been generated."""
        lower = text.lower()
        rec_data = self.last_recommendation
        if not rec_data or not rec_data.get("top_matches"):
            return self.reset()

        top_matches = rec_data["top_matches"]
        best = top_matches[0]
        lap = best["laptop"]

        # Follow-up: Why this laptop?
        if "why" in lower and ("choose" in lower or "select" in lower or "this" in lower or "laptop" in lower or "recommend" in lower):
            breakdown = best["sub_scores"]
            lines = [
                f"🤖 **Inference Engine Rule Analysis for {lap['name']}:**",
                f"- **Overall Score:** `{best['total_score']}/100`",
                f"- **Budget Weight (25%):** {breakdown['budget']}/25",
                f"- **Usage Fit (20%):** {breakdown['usage']}/20",
                f"- **RAM Weight (15%):** {breakdown['ram']}/15",
                f"- **CPU Performance (10%):** {breakdown['cpu']}/10",
                f"- **GPU Capability (10%):** {breakdown['gpu']}/10",
                f"- **Storage (5%):** {breakdown['storage']}/5",
                f"- **Battery (5%):** {breakdown['battery']}/5",
                f"- **Portability (5%):** {breakdown['portability']}/5",
                f"- **Display (5%):** {breakdown['display']}/5\n",
                "**Fired Expert Rules:** " + (", ".join(best["fired_rules"]) if best["fired_rules"] else "Standard heuristic weights"),
                "\n**Key Advantages:**",
                "\n".join([f"✓ {r}" for r in best["matched_reasons"][:5]])
            ]
            return {
                "reply": "\n".join(lines),
                "options": ["Compare top 2 laptops", "Show alternatives", "Show cheaper options", "Restart"],
                "status": "follow_up"
            }

        # Follow-up: Is it good for gaming?
        if "gaming" in lower or "game" in lower or "fps" in lower or "play" in lower:
            gpu = lap["gpu"]
            refresh = lap["refresh_rate"]
            is_dedicated = "RTX" in gpu or "GTX" in gpu or lap["gpu_score"] >= 70
            if is_dedicated and refresh >= 120:
                reply = (
                    f"🎮 **Gaming Verdict for {lap['name']}:**\n"
                    f"Yes! It is well-suited for gaming. It features a dedicated **{gpu}** graphics card "
                    f"and a smooth **{refresh}Hz** display, comfortably handling modern titles like Valorant, GTA V, "
                    f"Forza Horizon, and Cyberpunk 2077 at 1080p."
                )
            elif is_dedicated:
                reply = (
                    f"🎮 **Gaming Verdict for {lap['name']}:**\n"
                    f"Yes, it has a dedicated **{gpu}** which runs most games at medium-to-high settings, "
                    f"though the display runs at standard {refresh}Hz."
                )
            else:
                reply = (
                    f"🎮 **Gaming Verdict for {lap['name']}:**\n"
                    f"It has **{gpu}** (integrated graphics). While fine for casual 2D titles, Minecraft, or Roblox, "
                    f"it is **not recommended** for intensive 3D AAA gaming. If gaming is a priority, consider asking for a gaming laptop!"
                )
            return {
                "reply": reply,
                "options": ["Best gaming laptop", "Compare top 2 laptops", "Show alternatives", "Restart"],
                "status": "follow_up"
            }

        # Follow-up: Is it good for programming?
        if "program" in lower or "coding" in lower or "code" in lower or "developer" in lower:
            reply = (
                f"💻 **Programming Verdict for {lap['name']}:**\n"
                f"Absolutely! With {lap['ram']} GB of RAM and a {lap['processor']} (CPU Score: {lap['cpu_score']}/100), "
                f"it will easily handle VS Code, IntelliJ, Docker containers, local databases, and web dev servers without lag."
            )
            return {
                "reply": reply,
                "options": ["Why this laptop?", "Compare top 2 laptops", "Show alternatives", "Restart"],
                "status": "follow_up"
            }

        # Follow-up: Show cheaper options
        if "cheap" in lower or "lower budget" in lower or "less expensive" in lower or "save money" in lower:
            cheaper = [m for m in self.inference_engine.kb.laptops if m["price"] < lap["price"]]
            cheaper.sort(key=lambda x: x["price"])
            if cheaper:
                cheapest_list = cheaper[:3]
                lines = [
                    f"💰 **Top Cheaper Alternatives (under ₹{lap['price']:,}):**\n"
                ]
                for idx, c in enumerate(cheapest_list, start=1):
                    lines.append(
                        f"**{idx}. {c['name']}** — **₹{c['price']:,}** (Saves ₹{lap['price'] - c['price']:,})\n"
                        f"   - CPU: {c['processor']} | RAM: {c['ram']} GB | GPU: {c['gpu']}\n"
                        f"   - *{c['description']}*\n"
                    )
                lines.append("Would you like to compare any of these or restart?")
                return {
                    "reply": "\n".join(lines),
                    "options": ["Compare top 2 laptops", "Show alternatives", "Restart"],
                    "status": "follow_up"
                }
            else:
                return {
                    "reply": f"The {lap['name']} is already one of the most budget-conscious laptops available in our system!",
                    "options": ["Compare top 2 laptops", "Show alternatives", "Restart"],
                    "status": "follow_up"
                }

        # Follow-up: I want more RAM
        if "more ram" in lower or "32 gb" in lower or "32gb" in lower or "64 gb" in lower:
            high_ram = [m for m in self.inference_engine.kb.laptops if m["ram"] >= 32]
            if high_ram:
                lines = [
                    "🚀 **Laptops with 32 GB+ High Capacity RAM:**\n"
                ]
                for idx, h in enumerate(high_ram, start=1):
                    lines.append(
                        f"**{idx}. {h['name']}** — **₹{h['price']:,}**\n"
                        f"   - RAM: **{h['ram']} GB** | CPU: {h['processor']} | GPU: {h['gpu']}\n"
                        f"   - Primary Usage: {h['primary_usage']}\n"
                    )
                return {
                    "reply": "\n".join(lines),
                    "options": ["Compare top 2 laptops", "Show alternatives", "Restart"],
                    "status": "follow_up"
                }
            else:
                return {
                    "reply": "No laptops with >= 32GB were found in the current catalog.",
                    "options": ["Show alternatives", "Restart"],
                    "status": "follow_up"
                }

        # Follow-up: Show alternatives
        if "alt" in lower or "option" in lower or "other" in lower:
            alts = top_matches[1:]
            if alts:
                lines = ["🥈 **Alternative Recommendations Ranked by Compatibility:**\n"]
                for i, alt in enumerate(alts, start=1):
                    al = alt["laptop"]
                    icon = "🥈" if i == 1 else "🥉"
                    lines.append(
                        f"### {icon} Alternative {i}: **{al['name']}**\n"
                        f"- **Score:** `{alt['total_score']}/100` | **Price:** ₹{al['price']:,}\n"
                        f"- **Processor:** {al['processor']} | **RAM:** {al['ram']} GB | **Storage:** {al['storage']} GB SSD\n"
                        f"- **GPU:** {al['gpu']} | **Battery:** {al['battery']} hrs | **Weight:** {al['weight']} kg\n"
                        f"- **Why this alternative:** " + (alt["matched_reasons"][0] if alt["matched_reasons"] else al["description"]) + "\n"
                    )
                if rec_data.get("comparative_notes"):
                    lines.append("**Key Differences:**\n" + "\n".join([f"• {n}" for n in rec_data["comparative_notes"]]))
                return {
                    "reply": "\n".join(lines),
                    "options": ["Compare top 2 laptops", "Why this laptop?", "Show cheaper options", "Restart"],
                    "status": "follow_up"
                }
            else:
                return {
                    "reply": "There are no additional alternatives for your current filter criteria.",
                    "options": ["Restart"],
                    "status": "follow_up"
                }

        # Follow-up: Best gaming laptop
        if "best gaming" in lower:
            gaming_laptops = [l for l in self.inference_engine.kb.laptops if "Gaming" in l["primary_usage"] or "RTX" in l["gpu"]]
            gaming_laptops.sort(key=lambda x: (x["gpu_score"], x["cpu_score"]), reverse=True)
            top_g = gaming_laptops[0]
            return {
                "reply": (
                    f"🔥 **Absolute Best Gaming Laptop in Catalog:**\n\n"
                    f"**{top_g['name']}** (₹{top_g['price']:,})\n"
                    f"- **GPU:** {top_g['gpu']} (GPU Score: {top_g['gpu_score']}/100)\n"
                    f"- **CPU:** {top_g['processor']} (CPU Score: {top_g['cpu_score']}/100)\n"
                    f"- **RAM:** {top_g['ram']} GB\n"
                    f"- **Display:** {top_g['display']}\" {top_g['refresh_rate']}Hz\n"
                    f"- *{top_g['description']}*"
                ),
                "options": ["Compare top 2 laptops", "Show alternatives", "Restart"],
                "status": "follow_up"
            }

        # Follow-up: Compare laptops
        if "compare" in lower:
            if len(top_matches) >= 2:
                cmp_res = self.inference_engine.compare_laptops(top_matches[0]["laptop"]["id"], top_matches[1]["laptop"]["id"])
                return {
                    "reply": (
                        f"📊 **Head-to-Head Comparison: {top_matches[0]['laptop']['name']} vs {top_matches[1]['laptop']['name']}**\n\n"
                        f"{self._format_markdown_table(cmp_res['features'])}\n\n"
                        f"🎯 **Expert Conclusion:**\n{cmp_res['conclusion']}"
                    ),
                    "comparison": cmp_res,
                    "options": ["Why this laptop?", "Show cheaper options", "Show alternatives", "Restart"],
                    "status": "comparison"
                }
            else:
                return {
                    "reply": "I need at least 2 recommended laptops to generate a side-by-side comparison.",
                    "options": ["Restart"],
                    "status": "follow_up"
                }

        # If user expresses a new requirement or update (e.g. "budget is 80k")
        new_b = NLPExtractor.extract_budget(text)
        new_u = NLPExtractor.extract_usage(text)
        new_r = NLPExtractor.extract_ram(text)
        if new_b or new_u or new_r:
            if new_b:
                self.requirements["budget"] = new_b
            if new_u:
                self.requirements["usage"] = new_u
            if new_r:
                self.requirements["ram"] = new_r
            return self._generate_recommendation_response(prefix="🔄 I have updated your requirements!\n\n")

        # Fallback response for unhandled conversational turns
        return {
            "reply": (
                f"I'm here to help with your laptop selection! You can ask:\n"
                f"- *'Why this laptop?'*\n"
                f"- *'Compare top 2 laptops'*\n"
                f"- *'Is it good for gaming?'*\n"
                f"- *'Show cheaper options'*\n"
                f"- *'I want more RAM'*\n"
                f"- Or type `restart` to start fresh."
            ),
            "options": ["Why this laptop?", "Compare top 2 laptops", "Show cheaper options", "Restart"],
            "status": "follow_up"
        }

    def _format_markdown_table(self, features):
        rows = [
            "| Feature | Laptop 1 | Laptop 2 |",
            "| :--- | :--- | :--- |"
        ]
        for f in features:
            rows.append(f"| {f['feature']} | {f['lap1']} | {f['lap2']} |")
        return "\n".join(rows)
