import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import plotly.figure_factory as ff
import os
import vispy.scene
import vispy.io
import vispy.app
from vispy.scene import SceneCanvas, visuals
import tempfile
import webbrowser
import pandas as pd
import plotly.graph_objects as go

# Streamlit Page Configuration
st.set_page_config(page_title="AR/VR-Enhanced OS Learning", layout="wide")

# Sidebar Navigation
st.title("🔹 AR/VR-Enhanced OS Learning Platform")
st.sidebar.header("Navigation")
option = st.sidebar.radio("Select a topic:", ["Home", "Process Scheduling", "Memory Management", "AR/VR Visualization"])

# Home Page
if option == "Home":
    st.markdown("""
        <style>
            .centered {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
            }
            .title-style {
                font-size: 2.5rem;
                font-weight: 700;
                margin-top: 30px;
                color: #1f77b4;
            }
            .subtitle-style {
                font-size: 1.2rem;
                color: #555;
                margin-bottom: 20px;
            }
        </style>
        <div class="centered">
            <div class="title-style">👨‍💻 Welcome to the AR/VR OS Learning Platform! 👩‍💻</div>
            <div class="subtitle-style">Explore Operating System concepts with visual and interactive simulations.</div>
        </div>
    """, unsafe_allow_html=True)

    st.image("https://images.unsplash.com/photo-1516321318423-f06f85e504b3", use_column_width=True)

    st.markdown("### 📚 Features You Can Explore:")
    st.markdown("- 🔄 **Process Scheduling**: Visualize FCFS, SJF, and Round Robin with Gantt charts")
    st.markdown("- 💾 **Memory Management**: Simulate First-Fit, Best-Fit, Worst-Fit allocation")
    st.markdown("- 🧠 **AR/VR Visualization**: Dive into immersive 3D simulations of OS internals")

    st.markdown("---")
    st.markdown("💡 *Use the navigation sidebar to select a topic and begin your learning journey!*")

# Process Scheduling (Gantt Chart)
elif option == "Process Scheduling":
    st.subheader("🔄 Process Scheduling Simulation")

    num_processes = st.number_input("Enter number of processes:", min_value=1, max_value=5, step=1)
    processes = [f"P{i+1}" for i in range(num_processes)]
    burst_times = [st.number_input(f"Enter Burst Time for {p}:", min_value=1, max_value=20) for p in processes]
    arrival_times = [st.number_input(f"Enter Arrival Time for {p}:", min_value=0, max_value=20) for p in processes]

    # Select scheduling algorithm
    scheduling_algo = st.selectbox("Choose Scheduling Algorithm:", ["FCFS", "SJF", "Round Robin"])

    # FCFS Scheduling with Arrival Time
    def fcfs_scheduling(processes, burst_time, arrival_time):
        start_time = [0] * len(processes)
        completion_time = [0] * len(processes)
        turnaround_time = [0] * len(processes)
        waiting_time = [0] * len(processes)
        
        # Calculate start time and completion time
        for i in range(len(processes)):
            if i == 0:
                start_time[i] = max(0, arrival_time[i])
            else:
                start_time[i] = max(completion_time[i-1], arrival_time[i])
            completion_time[i] = start_time[i] + burst_time[i]
            turnaround_time[i] = completion_time[i] - arrival_time[i]
            waiting_time[i] = turnaround_time[i] - burst_time[i]

        # Create a DataFrame to display the table
        data = {
            "Process": processes,
            "Arrival Time (AT)": arrival_time,
            "Burst Time (BT)": burst_time,
            "Completion Time (CT)": completion_time,
            "Turnaround Time (TAT)": turnaround_time,
            "Waiting Time (WT)": waiting_time
        }
        
        df = pd.DataFrame(data)
        st.subheader("📊 Process Scheduling Table")
        st.dataframe(df)

        # Create a Gantt chart with Plotly
        fig = go.Figure()
        for i in range(len(processes)):
            fig.add_trace(go.Bar(
                y=[processes[i]],
                x=[burst_time[i]],
                orientation='h',
                base=start_time[i],
                hoverinfo='x+y+name',
                name=processes[i],
                marker=dict(color='skyblue')
            ))

        fig.update_layout(
            title="FCFS Scheduling Gantt Chart",
            xaxis_title="Time",
            yaxis_title="Process",
            barmode='stack',
            showlegend=False
        )
        st.plotly_chart(fig)

    # SJF Scheduling with Arrival Time
    def sjf_scheduling(processes, burst_time, arrival_time):
        # Sort processes by arrival time
        sorted_processes = sorted(zip(processes, burst_time, arrival_time), key=lambda x: x[2])
        sorted_names, sorted_times, sorted_arrivals = zip(*sorted_processes)
        
        start_time = [0] * len(sorted_processes)
        completion_time = [0] * len(sorted_processes)
        turnaround_time = [0] * len(sorted_processes)
        waiting_time = [0] * len(sorted_processes)
        
        completed = [False] * len(sorted_processes)
        current_time = 0
        remaining_processes = len(sorted_processes)
        
        while remaining_processes > 0:
            available_processes = [(i, sorted_times[i]) for i in range(len(sorted_processes)) 
                                 if not completed[i] and sorted_arrivals[i] <= current_time]
            
            if available_processes:
                next_process_idx = min(available_processes, key=lambda x: x[1])[0]
                
                start_time[next_process_idx] = current_time
                completion_time[next_process_idx] = current_time + sorted_times[next_process_idx]
                turnaround_time[next_process_idx] = completion_time[next_process_idx] - sorted_arrivals[next_process_idx]
                waiting_time[next_process_idx] = turnaround_time[next_process_idx] - sorted_times[next_process_idx]
                
                completed[next_process_idx] = True
                current_time = completion_time[next_process_idx]
                remaining_processes -= 1
            else:
                current_time = min(sorted_arrivals[i] for i in range(len(sorted_processes)) if not completed[i])
        
        # Create a DataFrame to display the table
        data = {
            "Process": sorted_names,
            "Arrival Time (AT)": sorted_arrivals,
            "Burst Time (BT)": sorted_times,
            "Completion Time (CT)": completion_time,
            "Turnaround Time (TAT)": turnaround_time,
            "Waiting Time (WT)": waiting_time
        }
        
        df = pd.DataFrame(data)
        st.subheader("📊 Process Scheduling Table")
        st.dataframe(df)
        
        # Create a Gantt chart with Plotly
        fig = go.Figure()
        for i in range(len(sorted_processes)):
            fig.add_trace(go.Bar(
                y=[sorted_names[i]],
                x=[sorted_times[i]],
                orientation='h',
                base=start_time[i],
                hoverinfo='x+y+name',
                name=sorted_names[i],
                marker=dict(color='lightcoral')
            ))
        
        fig.update_layout(
            title="SJF Scheduling Gantt Chart",
            xaxis_title="Time",
            yaxis_title="Process",
            barmode='stack',
            showlegend=False
        )
        st.plotly_chart(fig)

    # Round Robin Scheduling with Arrival Time
    def round_robin_scheduling(processes, burst_time, arrival_time, quantum=2):
        remaining_time = burst_time.copy()
        time = 0
        gantt_chart = []
        completion_time = [0] * len(processes)
        turnaround_time = [0] * len(processes)
        waiting_time = [0] * len(processes)
        queue = []

        while any(rt > 0 for rt in remaining_time):
            # Add newly arrived processes to queue
            for i, at in enumerate(arrival_time):
                if at <= time and remaining_time[i] > 0 and i not in queue:
                    queue.append(i)
            
            if queue:
                i = queue.pop(0)
                execution_time = min(quantum, remaining_time[i])
                gantt_chart.append((processes[i], time, time + execution_time))
                time += execution_time
                remaining_time[i] -= execution_time
                
                # Add process back to queue if not completed
                if remaining_time[i] > 0:
                    queue.append(i)
                
                # Update completion time for completed process
                if remaining_time[i] == 0:
                    completion_time[i] = time
            
            else:
                time += 1

        # Calculate Turnaround and Waiting Time
        for i in range(len(processes)):
            turnaround_time[i] = completion_time[i] - arrival_time[i]
            waiting_time[i] = turnaround_time[i] - burst_time[i]

        # Create a DataFrame to display the table
        data = {
            "Process": processes,
            "Arrival Time (AT)": arrival_time,
            "Burst Time (BT)": burst_time,
            "Completion Time (CT)": completion_time,
            "Turnaround Time (TAT)": turnaround_time,
            "Waiting Time (WT)": waiting_time
        }

        df = pd.DataFrame(data)
        st.subheader("📊 Process Scheduling Table")
        st.dataframe(df)

        # Create a Gantt chart with Plotly
        fig = go.Figure()
        for p, start, end in gantt_chart:
            fig.add_trace(go.Bar(
                y=[p],
                x=[end - start],
                orientation='h',
                base=start,
                hoverinfo='x+y+name',
                name=p,
                marker=dict(color='purple')
            ))

        fig.update_layout(
            title="Round Robin Scheduling Gantt Chart",
            xaxis_title="Time",
            yaxis_title="Process",
            barmode='stack',
            showlegend=False
        )
        st.plotly_chart(fig)

    # Simulate Button
    if st.button("Simulate"):
        if scheduling_algo == "FCFS":
            fcfs_scheduling(processes, burst_times, arrival_times)
        elif scheduling_algo == "SJF":
            sjf_scheduling(processes, burst_times, arrival_times)
        elif scheduling_algo == "Round Robin":
            round_robin_scheduling(processes, burst_times, arrival_times, quantum=4)

# Memory Management (3D Blocks)
elif option == "Memory Management":
    st.subheader("💾 Memory Allocation Strategies Visualization")

    # Input for Memory Blocks and Processes
    col1, col2 = st.columns(2)
    with col1:
        block_input = st.text_input("Enter Memory Blocks (comma-separated)", "100, 500, 200, 300, 600")
        blocks = [int(x.strip()) for x in block_input.split(",") if x.strip().isdigit()]

    with col2:
        process_input = st.text_input("Enter Process Sizes (comma-separated)", "212, 417, 112, 426")
        processes = [int(x.strip()) for x in process_input.split(",") if x.strip().isdigit()]

    strategy = st.radio("Select Allocation Strategy", ["First-Fit", "Best-Fit", "Worst-Fit"])

    # Allocation Algorithms
    def first_fit(blocks, processes):
        allocation = [-1] * len(processes)
        blocks_copy = blocks.copy()
        for i in range(len(processes)):
            for j in range(len(blocks_copy)):
                if blocks_copy[j] >= processes[i]:
                    allocation[i] = j
                    blocks_copy[j] -= processes[i]
                    break
        return allocation

    def best_fit(blocks, processes):
        allocation = [-1] * len(processes)
        blocks_copy = blocks.copy()
        for i in range(len(processes)):
            best_idx = -1
            min_space = float('inf')
            for j in range(len(blocks_copy)):
                if blocks_copy[j] >= processes[i] and blocks_copy[j] - processes[i] < min_space:
                    best_idx = j
                    min_space = blocks_copy[j] - processes[i]
            if best_idx != -1:
                allocation[i] = best_idx
                blocks_copy[best_idx] -= processes[i]
        return allocation

    def worst_fit(blocks, processes):
        allocation = [-1] * len(processes)
        blocks_copy = blocks.copy()
        for i in range(len(processes)):
            worst_idx = -1
            max_space = -1
            for j in range(len(blocks_copy)):
                if blocks_copy[j] >= processes[i] and blocks_copy[j] > max_space:
                    worst_idx = j
                    max_space = blocks_copy[j]
            if worst_idx != -1:
                allocation[i] = worst_idx
                blocks_copy[worst_idx] -= processes[i]
        return allocation

    # Simulate Allocation
    if st.button("Simulate Allocation"):
        original_blocks = blocks.copy()
        if strategy == "First-Fit":
            allocation = first_fit(blocks, processes)
        elif strategy == "Best-Fit":
            allocation = best_fit(blocks, processes)
        elif strategy == "Worst-Fit":
            allocation = worst_fit(blocks, processes)

        # Result Table
        result = []
        for i in range(len(processes)):
            result.append({
                "Process No": i + 1,
                "Process Size": processes[i],
                "Block Allocated": f"Block {allocation[i] + 1}" if allocation[i] != -1 else "Not Allocated"
            })

        st.subheader("📝 Allocation Result")
        st.dataframe(pd.DataFrame(result))

        # Visualization
        st.subheader("📊 Memory Allocation Chart")
        fig, ax = plt.subplots(figsize=(10, 4))
        y = 1
        for i in range(len(processes)):
            block_idx = allocation[i]
            if block_idx != -1:
                start = sum(original_blocks[:block_idx])
                ax.broken_barh([(start, processes[i])], (y-0.4, 0.8), facecolors='tab:blue')
                ax.text(start + processes[i]/2, y, f"P{i+1}", ha='center', va='center', color='white')

        # Draw memory blocks
        current = 0
        for i, block in enumerate(original_blocks):
            ax.broken_barh([(current, block)], (y-0.4, 0.8), facecolors='none', edgecolors='black')
            current += block

        ax.set_ylim(0, 2)
        ax.set_xlim(0, sum(original_blocks))
        ax.set_xlabel("Memory Size")
        ax.set_yticks([])
        ax.set_title("Memory Blocks and Process Allocation")
        st.pyplot(fig)

# AR/VR 3D Visualization for OS Concepts
elif option == "AR/VR Visualization":
    st.subheader("🕶 AR/VR 3D Process and Memory Management Visualization")

    # Web-Based VR (Three.js for interactive VR experience)
    def open_vr_scene():
        html_code = """
        <!DOCTYPE html>
        <head>
            <title>FCFS Conveyor Simulation</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <style>
                body { margin: 0; overflow: hidden; }
                #ui { 
                    position: absolute; 
                    top: 10px; 
                    left: 10px; 
                    color: white; 
                    background: rgba(0, 0, 0, 0.8); 
                    padding: 15px; 
                    font-family: Arial;
                    border-radius: 5px;
                }
                #controls { 
                    position: absolute; 
                    top: 10px; 
                    right: 10px; 
                    background: rgba(0, 0, 0, 0.8); 
                    padding: 10px; 
                    border-radius: 5px;
                }
                button { 
                    margin: 5px; 
                    padding: 8px 12px; 
                    cursor: pointer; 
                    background: #444; 
                    color: white; 
                    border: none; 
                    border-radius: 3px;
                }
                button:hover { background: #666; }
                #gantt { 
                    position: absolute; 
                    bottom: 10px; 
                    left: 10px; 
                    width: 50%; 
                    height: 100px; 
                    background: rgba(0, 0, 0, 0.8); 
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <div id="ui">
                <h3>FCFS Scheduling - Conveyor Belt</h3>
                <p>Green: Ready, Red: Running, Gray: Completed</p>
                <p>Processes: <span id="procCount">0</span></p>
                <p>Avg. Waiting Time: <span id="avgWait">0</span> ms</p>
                <p>Avg. Turnaround Time: <span id="avgTurn">0</span> ms</p>
            </div>
            <div id="controls">
                <button onclick="addProcess()">Add Process</button>
                <button onclick="resetSimulation()">Reset</button>
                <button onclick="togglePause()">Pause/Resume</button>
            </div>
            <canvas id="gantt"></canvas>
            <script>
                // Scene setup
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({ antialias: true });
                renderer.setSize(window.innerWidth, window.innerHeight);
                document.body.appendChild(renderer.domElement);

                // Lighting
                scene.add(new THREE.AmbientLight(0x404040));
                const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
                directionalLight.position.set(0, 5, 5);
                scene.add(directionalLight);

                // Process management
                let processes = [];
                let currentTime = 0;
                let isPaused = false;
                const maxBurstTime = 1000;
                let totalWaitingTime = 0;
                let totalTurnaroundTime = 0;

                // Process states
                const states = {
                    READY: { color: 0x00ff00, name: 'Ready' },
                    RUNNING: { color: 0xff0000, name: 'Running' },
                    COMPLETED: { color: 0x888888, name: 'Completed' }
                };

                // Conveyor belt
                const beltGeometry = new THREE.PlaneGeometry(20, 2);
                const beltMaterial = new THREE.MeshPhongMaterial({ color: 0x333333 });
                const belt = new THREE.Mesh(beltGeometry, beltMaterial);
                belt.rotation.x = -Math.PI / 2;
                belt.position.y = -1;
                scene.add(belt);

                // CPU representation
                const cpuGeometry = new THREE.BoxGeometry(1.5, 1.5, 1.5);
                const cpuMaterial = new THREE.MeshPhongMaterial({ color: 0x3333ff, wireframe: true });
                const cpu = new THREE.Mesh(cpuGeometry, cpuMaterial);
                cpu.position.set(-8, 0, 0);
                scene.add(cpu);

                // Text sprite for labels
                function createTextSprite(message) {
                    const canvas = document.createElement('canvas');
                    canvas.width = 128;
                    canvas.height = 32;
                    const context = canvas.getContext('2d');
                    context.font = 'Bold 20px Arial';
                    context.fillStyle = 'white';
                    context.fillText(message, 0, 20);
                    const texture = new THREE.CanvasTexture(canvas);
                    const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
                    const sprite = new THREE.Sprite(spriteMaterial);
                    sprite.scale.set(1, 0.25, 1);
                    return sprite;
                }

                // Gantt chart
                const ganttCanvas = document.getElementById('gantt');
                const ganttCtx = ganttCanvas.getContext('2d');
                let ganttHistory = [];

                function updateGantt() {
                    ganttCanvas.width = window.innerWidth * 0.5;
                    ganttCtx.fillStyle = 'rgba(0, 0, 0, 0.8)';
                    ganttCtx.fillRect(0, 0, ganttCanvas.width, ganttCanvas.height);
                    ganttCtx.font = '12px Arial';
                    ganttCtx.fillStyle = 'white';

                    let x = 0;
                    ganttHistory.forEach(entry => {
                        const width = (entry.duration / 100) * ganttCanvas.width;
                        ganttCtx.fillStyle = entry.color;
                        ganttCtx.fillRect(x, 20, width, 60);
                        ganttCtx.fillStyle = 'white';
                        ganttCtx.fillText(`P${entry.id}`, x + 5, 50);
                        x += width;
                    });

                    ganttCtx.fillStyle = 'white';
                    ganttCtx.fillText(`Time: ${(currentTime / 1000).toFixed(1)}s`, 10, 15);
                }

                // Add new process
                window.addProcess = function() {
                    const burstTime = Math.floor(Math.random() * maxBurstTime) + 200;
                    const geometry = new THREE.BoxGeometry(0.8, 0.8, 0.8);
                    const material = new THREE.MeshPhongMaterial({ color: states.READY.color });
                    const cube = new THREE.Mesh(geometry, material);
                    const index = processes.length;
                    cube.position.set(index * 2, 0, 0);
                    cube.userData = {
                        id: index + 1,
                        state: 'READY',
                        burstTime: burstTime,
                        remainingTime: burstTime,
                        arrivalTime: currentTime,
                        startTime: null,
                        waitingTime: 0,
                        turnaroundTime: 0
                    };

                    const label = createTextSprite(`P${index + 1}: ${burstTime}ms`);
                    label.position.set(index * 2, 1, 0);
                    scene.add(label);
                    cube.userData.label = label;

                    processes.push(cube);
                    scene.add(cube);
                    updateUI();
                };

                // Initialize processes
                function initializeProcesses() {
                    processes = [];
                    currentTime = 0;
                    totalWaitingTime = 0;
                    totalTurnaroundTime = 0;
                    ganttHistory = [];
                    scene.children = scene.children.filter(child => child === cpu || child === belt || child.type === 'Light');
                    for (let i = 0; i < 3; i++) addProcess();
                }

                // Update UI
                function updateUI() {
                    document.getElementById('procCount').textContent = processes.length;
                    const avgWait = processes.length > 0 ? (totalWaitingTime / processes.length / 1000).toFixed(2) : 0;
                    const avgTurn = processes.length > 0 ? (totalTurnaroundTime / processes.length / 1000).toFixed(2) : 0;
                    document.getElementById('avgWait').textContent = avgWait;
                    document.getElementById('avgTurn').textContent = avgTurn;
                }

                // Reset simulation
                window.resetSimulation = function() {
                    initializeProcesses();
                    isPaused = false;
                    updateUI();
                };

                // Toggle pause/resume
                window.togglePause = function() {
                    isPaused = !isPaused;
                };

                // Camera position
                camera.position.set(0, 3, 10);
                camera.lookAt(0, 0, 0);

                // Handle window resize
                window.addEventListener('resize', () => {
                    camera.aspect = window.innerWidth / window.innerHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(window.innerWidth, window.innerHeight);
                    updateGantt();
                });

                // Animation loop
                function animate() {
                    requestAnimationFrame(animate);

                    if (!isPaused) {
                        // FCFS Logic
                        const currentProcess = processes.find(p => p.userData.state === 'RUNNING') || 
                                            processes.find(p => p.userData.state === 'READY');

                        if (currentProcess && currentProcess.userData.state !== 'RUNNING') {
                            currentProcess.userData.state = 'RUNNING';
                            currentProcess.userData.startTime = currentTime;
                            currentProcess.material.color.set(states.RUNNING.color);
                            currentProcess.position.set(cpu.position.x, 0, 0);
                            currentProcess.userData.label.position.set(cpu.position.x, 1, 0);
                            ganttHistory.push({
                                id: currentProcess.userData.id,
                                color: '#ff0000',
                                duration: 0
                            });
                        }

                        if (currentProcess) {
                            const delta = 16.67; // Approx 60 FPS
                            currentProcess.userData.remainingTime -= delta;
                            currentTime += delta;
                            ganttHistory[ganttHistory.length - 1].duration += delta;

                            // Update waiting time
                            processes.forEach(p => {
                                if (p !== currentProcess && p.userData.state === 'READY') {
                                    p.userData.waitingTime += delta;
                                }
                            });

                            // Process completion
                            if (currentProcess.userData.remainingTime <= 0) {
                                currentProcess.userData.state = 'COMPLETED';
                                currentProcess.material.color.set(states.COMPLETED.color);
                                currentProcess.position.set(cpu.position.x, -2, 0);
                                currentProcess.userData.label.position.set(cpu.position.x, -1, 0);
                                currentProcess.userData.turnaroundTime = currentTime - currentProcess.userData.arrivalTime;
                                totalWaitingTime += currentProcess.userData.waitingTime;
                                totalTurnaroundTime += currentProcess.userData.turnaroundTime;
                                updateUI();
                            }

                            // Move queue
                            processes.forEach((p, i) => {
                                if (p.userData.state === 'READY') {
                                    p.position.x = i * 2;
                                    p.userData.label.position.x = i * 2;
                                }
                            });
                        }

                        // Animate
                        processes.forEach(cube => {
                            if (cube.userData.state === 'RUNNING') {
                                cube.rotation.x += 0.03;
                                cube.rotation.y += 0.03;
                                cube.scale.set(1.2, 1.2, 1.2);
                            } else {
                                cube.rotation.x += 0.01;
                                cube.rotation.y += 0.01;
                                cube.scale.set(1, 1, 1);
                            }
                        });

                        updateGantt();
                    }

                    renderer.render(scene, camera);
                }

                // Start simulation
                initializeProcesses();
                animate();
            </script>
        </body>
        </html>
        """

        # Write HTML to a temporary file
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
            f.write(html_code)
            temp_file_name = f.name

        # Open it in the default web browser
        webbrowser.open(f'file://{temp_file_name}')

    # Button to launch the VR Simulation
    if st.button("Launch VR OS Simulation"):
        open_vr_scene()

    # Interactive Memory Blocks 3D
    st.subheader("🌐 Interactive Memory Allocation in VR")
    st.write("In this section, explore how memory is allocated using different algorithms (First-Fit, Best-Fit, Worst-Fit).")
    st.write("Imagine a 3D grid where each memory block and process interacts dynamically in the AR/VR space.")
