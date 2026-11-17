# Adaptive Bandwidth Allocation & QoS Simulator for Mixed Network Traffic

A discrete-event network simulator in Python that models contention over a shared bottleneck link carrying real-time voice, video, and bulk data traffic. It evaluates and compares unmanaged **Best-Effort (FIFO)** delivery against **Quality of Service (QoS)** mechanisms combining **Strict Priority Queuing** and **Token Bucket Traffic Shaping**.

---

## 1. Problem Overview: The Real-World Story

Picture a common home or office network scenario:
- **7:45 PM:** You are on an HD video call with a colleague or friend. The audio is crisp, and the video stream is smooth.
- **7:46 PM:** Another device on the same local network initiates a 4GB game update or file download.
- **7:46:05 PM:** Your call instantly stutters. Audio turns robotic and cuts out, and video frames freeze and pixelate.

### Why This Happens at the Network Layer
By default, standard consumer routers operate on **Best-Effort Delivery**:
1. All incoming packets — whether an urgent 200-byte voice sample or a 1500-byte bulk file chunk — are placed into a single **First-In, First-Out (FIFO)** queue.
2. The aggressive bulk download floods the router's queue with large packets at full wire speed.
3. The time-sensitive voice/video packets get stuck behind dozens of large bulk packets in the queue, causing **Queuing Delay (Latency Spikes)**.
4. Variations in waiting time lead to severe delay variation (**Jitter**).
5. Once the router's buffer is full, incoming packets are dropped (**Tail Drop Packet Loss**).

### The Solution: Quality of Service (QoS)
This project implements the dual-mechanism QoS solution used in enterprise routers and ISPs:
1. **Strict Priority Queuing (PQ):** Latency-sensitive flows (Voice & Video) are routed to a dedicated High-Priority queue that the link scheduler always drains first.
2. **Token Bucket Traffic Shaping:** The bulk download is rate-limited and shaped to a sustained bandwidth cap (e.g., 60% of the link), ensuring sufficient link headroom remains open for bursty real-time streams.

---

## 2. System Architecture

```
                  [Traffic Generators]
               /           |           \
     Voice Stream     Video Stream     Bulk Download
    (200B, 20ms CBR)  (1000B, 30fps)  (1500B, 15 Mbps)
               \           |           /
                v          v          v
          +-------------------------------+
          |     Identical Packet Stream   |
          +-------------------------------+
                   /             \
                  /               \
                 v                 v
       [ Run A: Baseline ]     [ Run B: QoS Enabled ]
      +-------------------+   +------------------------------------+
      | Single FIFO Queue |   | Packet Classifier (DSCP Marking)   |
      |   (Tail Drop)     |   |  - High Queue: Voice & Video       |
      +-------------------+   |  - Low Queue: Bulk Download        |
                |             |  - Token Bucket Shaper (Rate Cap)  |
                v             |  - Strict Priority Scheduler       |
      [ 10 Mbps Bottleneck]   +------------------------------------+
                |                               |
                v                               v
      +------------------------------------------------------------+
      |               Metrics Collection & Evaluation             |
      |    - End-to-End Latency    - RFC 3550 Interarrival Jitter  |
      |    - Packet Loss Rate (%)  - Per-Flow Throughput (Mbps)   |
      +------------------------------------------------------------+
                                |
                                v
      +------------------------------------------------------------+
      |         Terminal Rich Dashboard & Matplotlib Charts        |
      +------------------------------------------------------------+
```

---

## 3. Implemented Algorithms & Standards

### 3.1 FIFO Queue (Baseline)
- Packets are served in exact arrival order.
- Finite queue depth ($B = 100$ packets).
- Packets arriving when the queue is full are dropped via **Tail Drop**.

### 3.2 Strict Priority Queuing (QoS)
- Two distinct queues:
  - **High-Priority Queue:** Latency-critical traffic (Voice with `DSCP EF`, Video with `DSCP AF41`).
  - **Low-Priority Queue:** Latency-tolerant traffic (Bulk with `DSCP CS0`).
- The link scheduler always checks and drains the high-priority queue first before servicing any low-priority packets.

### 3.3 Token Bucket Traffic Shaper (QoS)
- Enforces an average transmission rate ($r$) while allowing controlled bursts ($b$).
- Tokens are refilled continuously:
  $$\text{tokens} = \min\left(b, \text{tokens} + \Delta t \times \frac{r}{8}\right)$$
- Low-priority packets can only transmit if sufficient tokens exist in the bucket, preventing the bulk stream from overwhelming the link even when the high-priority queue is momentarily empty.

### 3.4 RFC 3550 Interarrival Jitter
Calculated in real time per RFC 3550:
$$D(i-1, i) = |(R_i - S_i) - (R_{i-1} - S_{i-1})|$$
$$J_i = J_{i-1} + \frac{D(i-1, i) - J_{i-1}}{16}$$
where $S$ is sender generation time and $R$ is receiver delivery time.

---

## 4. Project Directory Structure

```
CNcbp/
├── README.md                          # Project documentation
├── requirements.txt                   # Dependencies
├── run_simulation.py                  # Main execution entrypoint
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── packet.py                  # Packet dataclass & priority tags
│   │   └── flow.py                    # Voice, Video, and Bulk traffic generators
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── fifo_queue.py              # Baseline FIFO queue with tail-drop
│   │   ├── priority_queue.py          # Strict priority queue scheduler
│   │   └── token_bucket.py            # Token bucket rate limiter & shaper
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── discrete_event_sim.py      # Discrete-event simulation link engine
│   │   └── scenario_runner.py         # Dual-run comparative experiment runner
│   ├── metrics/
│   │   ├── __init__.py
│   │   ├── rfc3550.py                 # RFC 3550 standard jitter calculator
│   │   └── collector.py               # Statistical aggregator & trace exporter
│   └── visualization/
│       ├── __init__.py
│       ├── terminal_dashboard.py      # Rich terminal tables & ITU-T SLA evaluation
│       └── charts.py                  # Publication-quality Matplotlib plots
└── results/                           # Generated plots, CSV traces, and JSON summaries
```

---

## 5. Getting Started

### Prerequisites
Python 3.10+ with the following packages:
```bash
pip install -r requirements.txt
```

### Running the Simulator
To run the standard 30-second comparative simulation:
```bash
python run_simulation.py
```

### Command Line Options
You can customize the network scenario using CLI flags:
```bash
python run_simulation.py \
  --duration 30.0 \
  --link-mbps 10.0 \
  --bulk-start 5.0 \
  --bulk-end 25.0 \
  --bulk-mbps 15.0 \
  --shaper-mbps 6.0 \
  --buffer-size 100 \
  --output-dir results
```

| Flag | Default | Description |
|---|---|---|
| `--duration` | `30.0` | Total simulation duration (seconds) |
| `--link-mbps` | `10.0` | Bottleneck link capacity (Mbps) |
| `--propagation-ms` | `5.0` | Propagation delay across the link (ms) |
| `--bulk-start` | `5.0` | Time when bulk download starts (seconds) |
| `--bulk-end` | `25.0` | Time when bulk download ends (seconds) |
| `--bulk-mbps` | `15.0` | Offered load of competing bulk flow (Mbps) |
| `--shaper-mbps` | `6.0` | Token bucket sustained rate limit for bulk flow (Mbps) |
| `--shaper-burst-kb` | `30.0`| Token bucket burst capacity (KB) |
| `--buffer-size` | `100` | Maximum queue buffer capacity (packets) |
| `--seed` | `42` | Random seed for deterministic reproducibility |
| `--output-dir` | `results` | Output directory for charts, CSVs, and JSON files |
| `--no-plots` | `False` | Skip plot generation (terminal-only mode) |

---

## 6. Generated Artifacts & Visualizations

Running the simulation automatically outputs to the `results/` folder:
- **`executive_dashboard.png`**: 4-panel comprehensive dashboard showing Voice Latency, Voice Jitter, Buffer Occupancy, and Packet Loss % side-by-side.
- **`latency_comparison.png`**: Packet-by-packet latency over time comparing Baseline FIFO vs QoS Priority Queuing.
- **`jitter_comparison.png`**: RFC 3550 Voice Jitter over time against the ITU-T G.114 30ms tolerance limit.
- **`packet_loss_comparison.png`**: Cumulative packet drop counts showing how QoS eliminates voice/video drops.
- **`throughput_comparison.png`**: Bandwidth consumption over time showing how traffic shaping keeps the link balanced.
- **`baseline_packet_trace.csv` & `qos_packet_trace.csv`**: Full per-packet trace data with arrival times, queuing delays, and delivery timestamps.
- **`summary_metrics.json`**: Structured JSON report for programmatic evaluation or frontend integration.

---

## 7. Next Steps: Web Frontend

The simulation engine is fully decoupled from the presentation layer. In the next phase, a web dashboard (FastAPI backend + interactive UI) can directly invoke `ScenarioRunner` and stream real-time results via WebSockets or REST endpoints.
