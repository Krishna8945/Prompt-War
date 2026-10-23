document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Lucide Icons
    lucide.createIcons();

    // 2. Chart.js Setup for Arrhenius Decay Curve & Telemetry
    const ctx = document.getElementById('telemetryChart').getContext('2d');
    const telemetryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
            datasets: [
                {
                    label: 'Actual Temp (°C)',
                    data: [4.1, 4.2, 4.5, 7.2, 9.8, 11.8, 12.1],
                    borderColor: '#f87171',
                    backgroundColor: 'rgba(248, 113, 113, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3
                },
                {
                    label: 'Optimal Baseline (°C)',
                    data: [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0],
                    borderColor: '#22c55e',
                    borderDash: [5, 5],
                    borderWidth: 1.5,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { 
                    labels: { color: '#94a3b8', font: { size: 10 } } 
                }
            },
            scales: {
                x: { 
                    ticks: { color: '#64748b', font: { size: 10 } }, 
                    grid: { color: '#1e293b' } 
                },
                y: { 
                    ticks: { color: '#64748b', font: { size: 10 } }, 
                    grid: { color: '#1e293b' } 
                }
            }
        }
    });

    // 3. IoT Disruption Injection Simulator
    const triggerBtn = document.getElementById('trigger-disruption-btn');
    if (triggerBtn) {
        triggerBtn.addEventListener('click', () => {
            const currentTempEl = document.getElementById('telemetry-temp');
            const currentLifespanEl = document.getElementById('telemetry-lifespan');
            
            // Simulate sudden refrigeration compressor failure
            currentTempEl.textContent = "15.4 °C";
            currentLifespanEl.textContent = "1.8 Days";
            
            // Update live telemetry chart
            telemetryChart.data.labels.push('NOW');
            telemetryChart.data.datasets[0].data.push(15.4);
            telemetryChart.data.datasets[1].data.push(4.0);
            telemetryChart.update();

            alert("🚨 Refrigeration Failure Injected! Dynamic shelf life re-estimated to 1.8 Days. Click 'Run Agent Swarm' to initiate autonomous rerouting.");
        });
    }

    // 4. Multi-Agent Swarm Execution Simulator
    const runSwarmBtn = document.getElementById('run-swarm-btn');
    if (runSwarmBtn) {
        runSwarmBtn.addEventListener('click', () => {
            const traceContainer = document.getElementById('agent-trace-container');
            const now = new Date().toLocaleTimeString();

            const newLogs = `
                <div class="p-3 bg-slate-900/80 rounded-lg border border-slate-800/80 border-l-4 border-l-purple-500 animate-fade-in">
                    <div class="flex items-center justify-between text-[11px] text-slate-400 mb-1">
                        <span class="font-bold text-purple-400 flex items-center gap-1.5">
                            <i data-lucide="shield-alert" class="w-3.5 h-3.5"></i>
                            Agent 4: Autonomous ESG & Compliance Auditor
                        </span>
                        <span>${now}</span>
                    </div>
                    <div class="text-slate-300 font-sans text-xs">
                        <strong>Thought:</strong> Validating diversion route compliance with FDA FSMA Food Safety regulations and Scope 3 waste metrics.
                    </div>
                    <div class="mt-1 text-slate-400 font-sans text-[11px] bg-slate-950 p-1.5 rounded border border-slate-800">
                        <strong>Action:</strong> APPROVED -> 18.5 tons diverted to St. Louis Local Hub. Avoided 46.25 MT CO2e.
                    </div>
                </div>
            `;
            traceContainer.insertAdjacentHTML('afterbegin', newLogs);
            lucide.createIcons();
        });
    }

    // 5. Gemini AI Playbook Generator
    const generatePlaybookBtn = document.getElementById('generate-playbook-btn');
    if (generatePlaybookBtn) {
        generatePlaybookBtn.addEventListener('click', () => {
            const outputEl = document.getElementById('playbook-output');
            outputEl.classList.remove('hidden');
            outputEl.innerHTML = `<span class="text-purple-400">🤖 Querying Gemini 3 Flash Preview Agent...</span>`;

            setTimeout(() => {
                outputEl.innerHTML = `<strong>Gemini 3 Flash Strategic Action Plan:</strong>\n
1. <strong>Immediate Containment:</strong> Issue automated dispatch order to re-tune compressor settings to max power (+2.0°C target).\n
2. <strong>Logistics Diversion:</strong> Re-route Truck #402 to St. Louis Receiving Terminal (ETA: 1.1 Days vs Remaining Life: 1.8 Days).\n
3. <strong>Automated Clearing:</strong> Post batch to secondary grocery discount network at 25% price reduction.\n
4. <strong>ESG Accounting:</strong> Save 18.5 tons organic produce from landfill disposal.`;
            }, 1200);
        });
    }

    // 6. Modal Controls for Backend Code Viewer
    const modal = document.getElementById('backend-modal');
    const backendCodeBtn = document.getElementById('backend-code-btn');
    const closeModalBtn = document.getElementById('close-modal-btn');

    if (backendCodeBtn && modal) {
        backendCodeBtn.addEventListener('click', () => modal.classList.remove('hidden'));
    }
    if (closeModalBtn && modal) {
        closeModalBtn.addEventListener('click', () => modal.classList.add('hidden'));
    }
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.add('hidden');
        });
    }
});