import os
import json
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

# Initialize Gemini Client (Uses GEMINI_API_KEY environment variable)
gemini_client = None
if os.environ.get("GEMINI_API_KEY"):
    gemini_client = genai.Client()

# Sample In-Memory Database for Batches
BATCHES_DB = {
    "BATCH-9082": {
        "id": "BATCH-9082",
        "commodity": "Organic Avocados",
        "origin": "Michoacán, MX",
        "destination": "Chicago, IL",
        "quantity_tons": 18.5,
        "base_temp_c": 4.2,
        "current_temp_c": 11.8,
        "ethylene_ppm": 8.4,
        "humidity_pct": 89.0,
        "nominal_shelf_life_days": 14,
        "remaining_days_calc": 3.2,
        "status": "CRITICAL",
        "risk_score": 88
    },
    "BATCH-4019": {
        "id": "BATCH-4019",
        "commodity": "Fresh Strawberries",
        "origin": "Salinas, CA",
        "destination": "Denver, CO",
        "quantity_tons": 8.2,
        "base_temp_c": 2.0,
        "current_temp_c": 2.8,
        "ethylene_ppm": 0.5,
        "humidity_pct": 92.5,
        "nominal_shelf_life_days": 7,
        "remaining_days_calc": 6.1,
        "status": "OPTIMAL",
        "risk_score": 12
    }
}

# -------------------------------------------------------------------
# KINETIC SHELF-LIFE SIMULATION ENGINE (Arrhenius Reaction Kinetics)
# -------------------------------------------------------------------
def calculate_shelf_life(temp_c, ethylene_ppm, humidity, base_days=14):
    """
    Calculates decay acceleration based on temperature delta and ethylene exposure.
    Q10 temperature coefficient factor approx = 2.0 for every 10C rise.
    """
    q10 = 2.1
    temp_ref = 4.0  # Reference ideal temp in Celsius
    
    # Accelerated degradation rate
    temp_factor = q10 ** ((temp_c - temp_ref) / 10.0)
    ethylene_factor = 1.0 + (ethylene_ppm * 0.18)
    humidity_penalty = 1.2 if humidity > 95 or humidity < 75 else 1.0
    
    overall_decay_rate = temp_factor * ethylene_factor * humidity_penalty
    remaining_days = max(0.1, round(base_days / overall_decay_rate, 1))
    
    return {
        "decay_rate_multiplier": round(overall_decay_rate, 2),
        "remaining_shelf_life_days": remaining_days,
        "spoilage_risk_pct": min(100, int((overall_decay_rate / 4.0) * 100))
    }

# -------------------------------------------------------------------
# AGENTIC AGENT SWARM EXECUTION ENGINE
# -------------------------------------------------------------------
class AgenticOrchestrator:
    def __init__(self, batch_data):
        self.batch = batch_data
        self.logs = []

    def log(self, agent, thought, action, result):
        self.logs.append({
            "timestamp": datetime.utcnow().strftime("%H:%M:%S.%f")[:-3],
            "agent": agent,
            "thought": thought,
            "action": action,
            "result": result
        })

    def run_workflow(self):
        # Step 1: Telemetry Sentinel Agent
        self.log(
            "Telemetry Sentinel",
            f"Analyzing IoT sensor feeds for {self.batch['id']}. Temp: {self.batch['current_temp_c']}°C, Ethylene: {self.batch['ethylene_ppm']} ppm.",
            "EVALUATE_THRESHOLDS",
            f"ALERT: Temperature anomaly detected (+{round(self.batch['current_temp_c'] - self.batch['base_temp_c'], 1)}°C above baseline)."
        )

        # Step 2: Kinetic Shelf-Life Predictor Agent
        decay_metrics = calculate_shelf_life(
            self.batch['current_temp_c'],
            self.batch['ethylene_ppm'],
            self.batch['humidity_pct'],
            self.batch['nominal_shelf_life_days']
        )
        self.log(
            "Kinetic Predictor",
            "Applying Arrhenius thermal rate equation and gas cross-sensitivity models.",
            "RUN_KINETIC_MODEL",
            f"Remaining shelf-life reduced to {decay_metrics['remaining_shelf_life_days']} days (Decay Multiplier: {decay_metrics['decay_rate_multiplier']}x)."
        )

        # Step 3: Logistics & Reroute Optimizer Agent
        if decay_metrics['spoilage_risk_pct'] > 60:
            reroute_action = "REROUTE_LOCAL_FULFILLMENT"
            recommendation = "Divert shipment to nearest distribution hub in St. Louis; trigger immediate 25% dynamic markdown."
        else:
            reroute_action = "MAINTAIN_ROUTE"
            recommendation = "Maintain primary route to Chicago. Recommend re-icing cold storage unit at next depot."

        self.log(
            "Logistics Optimizer",
            "Checking transit vector against destination ETA vs recalculated kinetic expiry.",
            reroute_action,
            recommendation
        )

        # Step 4: ESG & Compliance Auditor Agent
        avoided_co2 = round(self.batch['quantity_tons'] * 2.5, 2)  # 2.5 t CO2e per ton food saved
        self.log(
            "ESG Auditor",
            "Calculating Scope 3 emissions prevention and potential organic methane generation penalty.",
            "AUDIT_ESG_IMPACT",
            f"Action prevents ~{self.batch['quantity_tons']} tons food waste, avoiding {avoided_co2} metric tons CO2e landfill emissions."
        )

        return {
            "decay_metrics": decay_metrics,
            "execution_trace": self.logs
        }

# -------------------------------------------------------------------
# REST API ENDPOINTS
# -------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ONLINE", "system": "EcoSupply AI Hub", "gemini_enabled": gemini_client is not None})

@app.route("/api/batches", methods=["GET"])
def get_batches():
    return jsonify(list(BATCHES_DB.values()))

@app.route("/api/batch/<batch_id>/analyze", methods=["POST"])
def analyze_batch(batch_id):
    batch = BATCHES_DB.get(batch_id)
    if not batch:
        return jsonify({"error": "Batch not found"}), 404

    # Update state if new sensor values provided
    data = request.json or {}
    if "current_temp_c" in data:
        batch["current_temp_c"] = float(data["current_temp_c"])
    if "ethylene_ppm" in data:
        batch["ethylene_ppm"] = float(data["ethylene_ppm"])

    orchestrator = AgenticOrchestrator(batch)
    results = orchestrator.run_workflow()

    return jsonify({
        "batch_id": batch_id,
        "status": "COMPLETED",
        "decay_analysis": results["decay_metrics"],
        "agent_trace": results["execution_trace"]
    })

@app.route("/api/gemini/playbook", methods=["POST"])
def generate_ai_playbook():
    """Generates automated mitigation playbooks using Gemini 3 Flash Preview"""
    data = request.json or {}
    batch_info = data.get("batch_info", "Batch #9082 Organic Produce experiencing thermal spike.")

    if not gemini_client:
        return jsonify({
            "playbook": "1. [Simulated Playbook] Immediately adjust refrigeration unit to +2.0°C.\n"
                        "2. Notify regional receiver for priority slot offloading.\n"
                        "3. Apply 20% automatic dynamic markdown on ERP system.",
            "model": "rule-based-fallback"
        })

    prompt = f"""You are an Autonomous Logistics & Perishable Cargo AI Agent.
Analyze the following cold chain incident and generate a structured operational playbook:
{json.dumps(batch_info)}

Provide:
1. Root Cause Assessment
2. Immediate Corrective Actions (Next 2 Hours)
3. Rerouting / Markdown Strategy
4. ESG & Waste Prevention Impact
Keep answers concise, authoritative, and actionable.
"""
    try:
        response = gemini_client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=600,
            )
        )
        return jsonify({"playbook": response.text, "model": "gemini-3-flash-preview"})
    except Exception as e:
        return jsonify({"error": str(e), "playbook": "Fallback Playbook: Issue alert to driver and route to nearest refrigeration service center."}), 500

if __name__ == "__main__":
    print("Starting EcoSupply Agentic Backend API...")
    app.run(host="0.0.0.0", port=5000, debug=True)