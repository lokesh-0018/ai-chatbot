"""
Expert System Module for Laptop Selection
Implements:
1. Knowledge Base (Laptop facts and specifications)
2. Rule Base (IF-THEN domain expert heuristics)
3. Inference Engine (Forward Chaining evaluation, scoring, XAI explanations)
"""

import math
from database import get_all_laptops, get_laptop_by_id


class Rule:
    """Represents a single production rule in the expert system."""
    def __init__(self, rule_id, name, description, condition, action):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.condition = condition  # Callable(requirements, laptop) -> bool
        self.action = action        # Callable(requirements, laptop, scores, explanations)


class RuleBase:
    """Contains domain expert rules for laptop evaluation."""
    def __init__(self):
        self.rules = []
        self._load_rules()

    def _load_rules(self):
        # 1. Programming Rule
        def cond_programming(req, lap):
            usage = req.get("usage", "").lower()
            return "program" in usage or "code" in usage or "dev" in usage

        def act_programming(req, lap, scores, explanations):
            # Programming needs CPU >= 75 and RAM >= 16 GB
            ram_match = lap["ram"] >= 16
            cpu_match = lap["cpu_score"] >= 75
            if ram_match and cpu_match:
                scores["usage"] = 20.0
                explanations["matched"].append("High-performance multi-core CPU and >=16GB RAM for compilation & IDEs")
            elif ram_match or cpu_match:
                scores["usage"] = 15.0
                explanations["matched"].append("Capable specs for standard programming workflows")
            else:
                scores["usage"] = 10.0
                explanations["limitations"].append("8GB RAM may feel tight for Docker, heavy IDEs, or virtualization")

        self.rules.append(Rule(
            "R_PROG",
            "Programming Optimization Rule",
            "IF usage is Programming AND RAM >= 16GB AND CPU >= Core i5/Ryzen 5 THEN maximize usage score.",
            cond_programming,
            act_programming
        ))

        # 2. Gaming Rule
        def cond_gaming(req, lap):
            usage = req.get("usage", "").lower()
            return "game" in usage or "gaming" in usage

        def act_gaming(req, lap, scores, explanations):
            is_dedicated_gpu = "RTX" in lap["gpu"] or "GTX" in lap["gpu"] or lap["gpu_score"] >= 70
            high_refresh = lap["refresh_rate"] >= 120
            ram_ok = lap["ram"] >= 16

            if is_dedicated_gpu and ram_ok and high_refresh:
                scores["usage"] = 20.0
                explanations["matched"].append(f"Dedicated {lap['gpu']} and {lap['refresh_rate']}Hz display for high FPS gaming")
            elif is_dedicated_gpu:
                scores["usage"] = 15.0
                explanations["matched"].append(f"Dedicated {lap['gpu']} graphics delivers solid gaming capability")
            else:
                scores["usage"] = 4.0
                explanations["limitations"].append("Integrated graphics cannot run modern AAA games smoothly")

        self.rules.append(Rule(
            "R_GAME",
            "Gaming GPU & Refresh Rate Rule",
            "IF usage is Gaming AND GPU >= RTX 3050 AND RAM >= 16GB THEN strongly increase usage score.",
            cond_gaming,
            act_gaming
        ))

        # 3. Video Editing Rule
        def cond_video(req, lap):
            usage = req.get("usage", "").lower()
            return "video" in usage or "edit" in usage or "render" in usage

        def act_video(req, lap, scores, explanations):
            has_gpu = "RTX" in lap["gpu"] or lap["gpu_score"] >= 65
            has_ram = lap["ram"] >= 16
            has_cpu = lap["cpu_score"] >= 80

            if has_gpu and has_ram and has_cpu:
                scores["usage"] = 20.0
                explanations["matched"].append("Hardware accelerated video rendering with dedicated GPU & fast CPU")
            elif has_ram and (has_gpu or has_cpu):
                scores["usage"] = 14.0
                explanations["matched"].append("Good for 1080p video editing, 4K timeline rendering may take longer")
            else:
                scores["usage"] = 7.0
                explanations["limitations"].append("Rendering 4K timelines or color grading requires more GPU/RAM power")

        self.rules.append(Rule(
            "R_VIDEO",
            "Video Editing Throughput Rule",
            "IF usage is Video Editing AND RAM >= 16GB AND dedicated GPU exists THEN increase usage score.",
            cond_video,
            act_video
        ))

        # 4. AI / Machine Learning Rule
        def cond_aiml(req, lap):
            usage = req.get("usage", "").lower()
            return "ai" in usage or "machine learning" in usage or "ml" in usage or "deep learning" in usage

        def act_aiml(req, lap, scores, explanations):
            has_nvidia_rtx = "RTX" in lap["gpu"]
            has_high_ram = lap["ram"] >= 32
            has_good_ram = lap["ram"] >= 16

            if has_nvidia_rtx and has_high_ram:
                scores["usage"] = 20.0
                explanations["matched"].append("NVIDIA CUDA Tensor cores with 32GB RAM for local model training & inference")
            elif has_nvidia_rtx and has_good_ram:
                scores["usage"] = 16.0
                explanations["matched"].append(f"NVIDIA {lap['gpu']} supports CUDA/cuDNN for ML workloads (16GB RAM)")
            elif has_good_ram:
                scores["usage"] = 9.0
                explanations["limitations"].append("Lacks dedicated NVIDIA CUDA GPU for GPU-accelerated deep learning")
            else:
                scores["usage"] = 5.0
                explanations["limitations"].append("Insufficient RAM and GPU for intensive AI/ML model execution")

        self.rules.append(Rule(
            "R_AIML",
            "AI / Machine Learning CUDA Acceleration Rule",
            "IF usage is AI/ML AND RAM >= 32GB AND NVIDIA RTX GPU exists THEN strongly increase usage score.",
            cond_aiml,
            act_aiml
        ))

        # 5. Student / Education Rule
        def cond_student(req, lap):
            usage = req.get("usage", "").lower()
            return "student" in usage or "education" in usage or "college" in usage or "school" in usage

        def act_student(req, lap, scores, explanations):
            good_battery = lap["battery"] >= 7.0
            portable = lap["weight"] <= 1.7
            budget_friendly = lap["price"] <= 65000

            if good_battery and portable:
                scores["usage"] = 20.0
                explanations["matched"].append(f"Campus-friendly: light ({lap['weight']}kg) with {lap['battery']}h long battery")
            elif portable or good_battery:
                scores["usage"] = 16.0
                explanations["matched"].append("Well-balanced portability and performance for college coursework")
            else:
                scores["usage"] = 12.0
                if lap["weight"] > 2.0:
                    explanations["limitations"].append(f"Heavier laptop ({lap['weight']}kg) to carry in a backpack daily")

        self.rules.append(Rule(
            "R_STUDENT",
            "Student Portability & Battery Rule",
            "IF usage is Student AND battery >= 7-8 hours AND weight <= 1.7kg THEN increase usage score.",
            cond_student,
            act_student
        ))

        # 6. Graphic Design Rule
        def cond_design(req, lap):
            usage = req.get("usage", "").lower()
            return "design" in usage or "graphic" in usage or "photoshop" in usage or "illustrator" in usage

        def act_design(req, lap, scores, explanations):
            has_gpu = lap["gpu_score"] >= 60
            has_ram = lap["ram"] >= 16
            if has_gpu and has_ram:
                scores["usage"] = 20.0
                explanations["matched"].append("Excellent display clarity and GPU acceleration for creative suites")
            elif has_ram:
                scores["usage"] = 15.0
                explanations["matched"].append("Sufficient memory for UI/UX and 2D vector graphic design")
            else:
                scores["usage"] = 8.0
                explanations["limitations"].append("8GB RAM may experience stutter in complex multi-layered art projects")

        self.rules.append(Rule(
            "R_DESIGN",
            "Graphic Design Display & Precision Rule",
            "IF usage is Graphic Design AND RAM >= 16GB AND good GPU THEN increase usage score.",
            cond_design,
            act_design
        ))

        # 7. Office Work / General Use Rule
        def cond_office(req, lap):
            usage = req.get("usage", "").lower()
            return "office" in usage or "general" in usage or "daily" in usage or "work" in usage or usage == ""

        def act_office(req, lap, scores, explanations):
            if lap["battery"] >= 7.0 and lap["weight"] <= 1.8:
                scores["usage"] = 20.0
                explanations["matched"].append("Smooth office productivity, spreadsheets, and conference calls")
            else:
                scores["usage"] = 16.0
                explanations["matched"].append("Reliable performance for daily computing tasks")

        self.rules.append(Rule(
            "R_OFFICE",
            "Office Work & Everyday Multitasking Rule",
            "IF usage is Office Work or General Use THEN assign balanced usage score.",
            cond_office,
            act_office
        ))


class KnowledgeBase:
    """Encapsulates laptop data facts retrieved from the database."""
    def __init__(self, db_path=None):
        self.db_path = db_path
        self.laptops = []
        self.reload()

    def reload(self):
        self.laptops = get_all_laptops(self.db_path)
        return self.laptops

    def get_by_id(self, laptop_id):
        return get_laptop_by_id(laptop_id, self.db_path)


class InferenceEngine:
    """
    Expert System Inference Engine.
    Executes Forward Chaining over the Rule Base against the Knowledge Base facts.
    Calculates weighted compatibility scores (0 - 100) and produces Explainable AI (XAI) reports.
    """
    WEIGHTS = {
        "budget": 25.0,
        "usage": 20.0,
        "ram": 15.0,
        "cpu": 10.0,
        "gpu": 10.0,
        "storage": 5.0,
        "battery": 5.0,
        "portability": 5.0,
        "display": 5.0
    }

    def __init__(self, db_path=None):
        self.kb = KnowledgeBase(db_path)
        self.rule_base = RuleBase()

    def evaluate_laptop(self, laptop, requirements):
        """
        Evaluates a single laptop against user requirements using forward chaining.
        Returns compatibility score (0-100), sub-scores, matched pros, and limitations.
        """
        scores = {k: 0.0 for k in self.WEIGHTS.keys()}
        explanations = {
            "matched": [],
            "limitations": [],
            "fired_rules": []
        }

        user_budget = requirements.get("budget")
        user_ram = requirements.get("ram")
        user_storage = requirements.get("storage")
        user_gpu = (requirements.get("gpu") or "").lower()
        user_cpu_pref = (requirements.get("processor") or "").lower()
        user_battery = (requirements.get("battery") or "").lower()
        user_portability = (requirements.get("portability") or "").lower()

        # ==================== 1. BUDGET SCORING (25%) ====================
        lap_price = laptop["price"]
        if user_budget is not None and user_budget > 0:
            if lap_price <= user_budget:
                # Within budget! Full 25 points, with small bonus if very cost-effective
                scores["budget"] = 25.0
                savings = user_budget - lap_price
                if savings >= 5000:
                    explanations["matched"].append(f"Well within your ₹{user_budget:,} budget (saves ₹{savings:,})")
                else:
                    explanations["matched"].append(f"Fits comfortably inside your ₹{user_budget:,} budget")
            elif lap_price <= user_budget * 1.08:
                # Slight stretch (up to 8% above budget)
                scores["budget"] = 16.0
                explanations["limitations"].append(f"Slightly over budget by ₹{lap_price - user_budget:,}")
            elif lap_price <= user_budget * 1.20:
                # Moderate stretch (up to 20% above budget)
                scores["budget"] = 8.0
                explanations["limitations"].append(f"Exceeds budget by ₹{lap_price - user_budget:,}")
            else:
                # Far over budget
                scores["budget"] = 2.0
                explanations["limitations"].append(f"Significantly exceeds your ₹{user_budget:,} budget")
        else:
            # No strict budget specified
            scores["budget"] = 22.0

        # ==================== 2. USAGE SCORING & RULE BASE (20%) ====================
        rule_fired = False
        for rule in self.rule_base.rules:
            if rule.condition(requirements, laptop):
                rule.action(requirements, laptop, scores, explanations)
                explanations["fired_rules"].append(rule.name)
                rule_fired = True
                break

        if not rule_fired:
            scores["usage"] = 15.0

        # ==================== 3. RAM SCORING (15%) ====================
        lap_ram = laptop["ram"]
        if user_ram:
            if lap_ram >= user_ram:
                scores["ram"] = 15.0
                if lap_ram > user_ram:
                    explanations["matched"].append(f"Generous {lap_ram} GB RAM (exceeds your {user_ram} GB requirement)")
                else:
                    explanations["matched"].append(f"Exact {lap_ram} GB RAM match for smooth multitasking")
            elif lap_ram >= user_ram // 2:
                scores["ram"] = 7.5
                explanations["limitations"].append(f"Has {lap_ram} GB RAM instead of requested {user_ram} GB")
            else:
                scores["ram"] = 3.0
                explanations["limitations"].append(f"Only {lap_ram} GB RAM (below {user_ram} GB requested)")
        else:
            if lap_ram >= 16:
                scores["ram"] = 15.0
            else:
                scores["ram"] = 10.0

        # ==================== 4. CPU SCORING (10%) ====================
        # Base CPU score based on benchmark tier (cpu_score out of 100)
        cpu_base = (laptop["cpu_score"] / 100.0) * 10.0

        # Check processor brand preference (Intel / AMD / Apple / No preference)
        lap_cpu_lower = laptop["processor"].lower()
        if "intel" in user_cpu_pref:
            if "intel" in lap_cpu_lower or "core" in lap_cpu_lower:
                cpu_base = min(10.0, cpu_base + 1.0)
                explanations["matched"].append(f"Matches your Intel preference ({laptop['processor']})")
            else:
                cpu_base = max(4.0, cpu_base - 1.5)
        elif "amd" in user_cpu_pref or "ryzen" in user_cpu_pref:
            if "amd" in lap_cpu_lower or "ryzen" in lap_cpu_lower:
                cpu_base = min(10.0, cpu_base + 1.0)
                explanations["matched"].append(f"Matches your AMD Ryzen preference ({laptop['processor']})")
            else:
                cpu_base = max(4.0, cpu_base - 1.5)
        else:
            if laptop["cpu_score"] >= 85:
                explanations["matched"].append(f"High-tier processor: {laptop['processor']}")

        scores["cpu"] = round(min(10.0, max(0.0, cpu_base)), 1)

        # ==================== 5. GPU SCORING (10%) ====================
        lap_gpu = laptop["gpu"].lower()
        is_dedicated = "rtx" in lap_gpu or "gtx" in lap_gpu or laptop["gpu_score"] >= 70

        if "no gpu" in user_gpu or "integrated" in user_gpu:
            if not is_dedicated:
                scores["gpu"] = 10.0
                explanations["matched"].append("Energy-efficient integrated graphics (cool & quiet operation)")
            else:
                scores["gpu"] = 7.0  # Has dedicated, which uses slightly more battery
        elif "rtx 4070" in user_gpu:
            if "4070" in lap_gpu or "4080" in lap_gpu:
                scores["gpu"] = 10.0
                explanations["matched"].append(f"Top-tier graphics: {laptop['gpu']}")
            elif "4060" in lap_gpu:
                scores["gpu"] = 8.0
            elif "4050" in lap_gpu:
                scores["gpu"] = 6.0
            else:
                scores["gpu"] = 2.0
                explanations["limitations"].append(f"Has {laptop['gpu']}, lower than requested RTX 4070+")
        elif "rtx 4060" in user_gpu:
            if "4060" in lap_gpu or "4070" in lap_gpu:
                scores["gpu"] = 10.0
                explanations["matched"].append(f"Matches requested RTX 4060 class GPU ({laptop['gpu']})")
            elif "4050" in lap_gpu or "3050" in lap_gpu:
                scores["gpu"] = 7.0
            else:
                scores["gpu"] = 2.0
                explanations["limitations"].append("Lacks RTX 4060 GPU")
        elif "rtx 4050" in user_gpu:
            if "4050" in lap_gpu or "4060" in lap_gpu or "4070" in lap_gpu:
                scores["gpu"] = 10.0
                explanations["matched"].append(f"Meets RTX 4050+ graphics requirement ({laptop['gpu']})")
            elif "3050" in lap_gpu:
                scores["gpu"] = 7.0
            else:
                scores["gpu"] = 3.0
                explanations["limitations"].append("Lacks dedicated RTX graphics card")
        elif "rtx 3050" in user_gpu:
            if is_dedicated:
                scores["gpu"] = 10.0
                explanations["matched"].append(f"Equipped with dedicated {laptop['gpu']}")
            else:
                scores["gpu"] = 3.0
                explanations["limitations"].append("Has integrated GPU instead of requested dedicated card")
        else:
            # No strong preference
            scores["gpu"] = round((laptop["gpu_score"] / 100.0) * 10.0, 1)

        # ==================== 6. STORAGE SCORING (5%) ====================
        lap_storage = laptop["storage"]
        if user_storage:
            if lap_storage >= user_storage:
                scores["storage"] = 5.0
                storage_label = f"{lap_storage} GB" if lap_storage < 1000 else f"{lap_storage // 1024} TB"
                explanations["matched"].append(f"Fast {storage_label} NVMe SSD storage")
            else:
                scores["storage"] = 2.5
                explanations["limitations"].append(f"Has {lap_storage} GB SSD instead of {user_storage} GB")
        else:
            scores["storage"] = 5.0 if lap_storage >= 512 else 3.0

        # ==================== 7. BATTERY SCORING (5%) ====================
        lap_battery = laptop["battery"]
        if "high" in user_battery:
            if lap_battery >= 8.5:
                scores["battery"] = 5.0
                explanations["matched"].append(f"Outstanding {lap_battery}h long-lasting battery life")
            elif lap_battery >= 6.5:
                scores["battery"] = 3.5
            else:
                scores["battery"] = 2.0
                explanations["limitations"].append(f"Modest {lap_battery}h battery (high performance drain)")
        elif "average" in user_battery:
            if lap_battery >= 6.0:
                scores["battery"] = 5.0
            else:
                scores["battery"] = 3.0
        else:
            # Basic / No preference
            scores["battery"] = min(5.0, (lap_battery / 10.0) * 5.0)

        # ==================== 8. PORTABILITY SCORING (5%) ====================
        lap_weight = laptop["weight"]
        if "very" in user_portability or "light" in user_portability:
            if lap_weight <= 1.4:
                scores["portability"] = 5.0
                explanations["matched"].append(f"Featherweight {lap_weight} kg ultralight chassis")
            elif lap_weight <= 1.8:
                scores["portability"] = 3.5
            else:
                scores["portability"] = 1.5
                explanations["limitations"].append(f"Heavier {lap_weight} kg chassis; less portable")
        elif "moderate" in user_portability:
            if lap_weight <= 2.2:
                scores["portability"] = 5.0
            else:
                scores["portability"] = 3.0
        else:
            # Not important
            scores["portability"] = 5.0

        # ==================== 9. DISPLAY SCORING (5%) ====================
        disp_score = 3.0
        if laptop["refresh_rate"] >= 120:
            disp_score += 1.0
            explanations["matched"].append(f"Fluid {laptop['refresh_rate']}Hz high refresh rate screen")
        if "OLED" in laptop.get("description", "") or "Retina" in laptop.get("description", ""):
            disp_score += 1.0
            explanations["matched"].append("Vibrant premium OLED/Retina panel with superior color gamut")
        scores["display"] = min(5.0, disp_score)

        # Total Compatibility Score (0 - 100)
        total_score = sum(scores.values())
        total_score = max(0, min(100, int(round(total_score))))

        # Deduplicate explanations while maintaining order
        def dedup(lst):
            seen = set()
            res = []
            for item in lst:
                if item not in seen:
                    seen.add(item)
                    res.append(item)
            return res

        return {
            "laptop": laptop,
            "total_score": total_score,
            "sub_scores": scores,
            "matched_reasons": dedup(explanations["matched"]),
            "limitations": dedup(explanations["limitations"]),
            "fired_rules": explanations["fired_rules"]
        }

    def recommend(self, requirements, top_n=3):
        """
        Runs inference over all laptops and returns top ranked recommendations
        with Explainable AI (XAI) comparative reasoning.
        """
        self.kb.reload()
        evaluated = []

        for laptop in self.kb.laptops:
            res = self.evaluate_laptop(laptop, requirements)
            evaluated.append(res)

        # Sort descending by total_score, tie-breaking by closer to budget and higher cpu_score
        def sort_key(item):
            lap = item["laptop"]
            budget = requirements.get("budget") or 1000000
            price_diff = abs(budget - lap["price"])
            return (item["total_score"], -price_diff, lap["cpu_score"])

        evaluated.sort(key=sort_key, reverse=True)

        top_matches = evaluated[:top_n]

        # Generate comparative Explainable AI explanations
        comparative_notes = []
        if len(top_matches) > 1:
            best = top_matches[0]["laptop"]
            alt1 = top_matches[1]["laptop"]
            if alt1["price"] < best["price"]:
                diff = best["price"] - alt1["price"]
                comparative_notes.append(f"Alternative 1 ({alt1['name']}) is ₹{diff:,} cheaper, offering high value.")
            elif alt1["price"] > best["price"]:
                comparative_notes.append(f"Alternative 1 ({alt1['name']}) has slightly higher specs at a premium price.")

        if len(top_matches) > 2:
            alt2 = top_matches[2]["laptop"]
            if alt2["ram"] > top_matches[0]["laptop"]["ram"]:
                comparative_notes.append(f"Alternative 2 ({alt2['name']}) provides higher RAM ({alt2['ram']} GB).")
            elif alt2["battery"] > top_matches[0]["laptop"]["battery"]:
                comparative_notes.append(f"Alternative 2 ({alt2['name']}) delivers longer battery life ({alt2['battery']} hours).")
            else:
                comparative_notes.append(f"Alternative 2 ({alt2['name']}) offers an alternative hardware balance.")

        return {
            "top_matches": top_matches,
            "comparative_notes": comparative_notes,
            "total_evaluated": len(evaluated)
        }

    def compare_laptops(self, laptop_id_1, laptop_id_2):
        """
        Generates a feature-by-feature comparison table between two laptops
        and draws an expert conclusion.
        """
        lap1 = self.kb.get_by_id(laptop_id_1)
        lap2 = self.kb.get_by_id(laptop_id_2)

        if not lap1 or not lap2:
            return None

        # Build comparison metrics
        def format_storage(s):
            return f"{s // 1024} TB SSD" if s >= 1000 else f"{s} GB SSD"

        features = [
            {"feature": "Brand", "lap1": lap1["brand"], "lap2": lap2["brand"]},
            {"feature": "Price", "lap1": f"₹{lap1['price']:,}", "lap2": f"₹{lap2['price']:,}"},
            {"feature": "Processor", "lap1": lap1["processor"], "lap2": lap2["processor"]},
            {"feature": "RAM", "lap1": f"{lap1['ram']} GB", "lap2": f"{lap2['ram']} GB"},
            {"feature": "Graphics (GPU)", "lap1": lap1["gpu"], "lap2": lap2["gpu"]},
            {"feature": "Storage", "lap1": format_storage(lap1["storage"]), "lap2": format_storage(lap2["storage"])},
            {"feature": "Display", "lap1": f'{lap1["display"]}" ({lap1["refresh_rate"]}Hz)', "lap2": f'{lap2["display"]}" ({lap2["refresh_rate"]}Hz)'},
            {"feature": "Battery Life", "lap1": f"{lap1['battery']} hrs", "lap2": f"{lap2['battery']} hrs"},
            {"feature": "Weight", "lap1": f"{lap1['weight']} kg", "lap2": f"{lap2['weight']} kg"},
            {"feature": "Primary Usage", "lap1": lap1["primary_usage"], "lap2": lap2["primary_usage"]}
        ]

        # Draw AI expert conclusion
        conclusions = []
        if lap1["price"] < lap2["price"]:
            conclusions.append(f"**{lap1['name']}** is more budget-friendly (saves ₹{lap2['price'] - lap1['price']:,}).")
        elif lap2["price"] < lap1["price"]:
            conclusions.append(f"**{lap2['name']}** is more budget-friendly (saves ₹{lap1['price'] - lap2['price']:,}).")

        if lap1["gpu_score"] > lap2["gpu_score"]:
            conclusions.append(f"**{lap1['name']}** has stronger graphics performance with its {lap1['gpu']}.")
        elif lap2["gpu_score"] > lap1["gpu_score"]:
            conclusions.append(f"**{lap2['name']}** has stronger graphics performance with its {lap2['gpu']}.")

        if lap1["battery"] > lap2["battery"]:
            conclusions.append(f"**{lap1['name']}** offers superior mobility with {lap1['battery']} hours of battery.")
        elif lap2["battery"] > lap1["battery"]:
            conclusions.append(f"**{lap2['name']}** offers superior mobility with {lap2['battery']} hours of battery.")

        conclusion_text = " ".join(conclusions) if conclusions else "Both laptops offer very comparable capabilities."

        return {
            "laptop1": lap1,
            "laptop2": lap2,
            "features": features,
            "conclusion": conclusion_text
        }
