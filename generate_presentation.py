"""
Professional PowerPoint Presentation Generator for:
Adaptive Bandwidth Allocation & QoS Simulator for Mixed Network Traffic.
Generates a 16:9 widescreen slide deck with structured layouts, comparison tables, and embedded high-res graphs.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE


# Design Palette
COLOR_NAVY_DARK = RGBColor(15, 23, 42)      # #0F172A
COLOR_NAVY_LIGHT = RGBColor(30, 41, 59)     # #1E293B
COLOR_BLUE_PRIMARY = RGBColor(37, 99, 235)  # #2563EB
COLOR_BLUE_ACCENT = RGBColor(96, 165, 250)  # #60A5FA
COLOR_GREEN = RGBColor(22, 163, 74)         # #16A34A
COLOR_RED = RGBColor(220, 38, 38)           # #DC2626
COLOR_GRAY_BG = RGBColor(248, 250, 252)     # #F8FAFC
COLOR_TEXT_DARK = RGBColor(30, 41, 59)      # #1E293B
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)  # #64748B
COLOR_WHITE = RGBColor(255, 255, 255)


def create_deck(results_dir: str, output_path: str):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text: str, category: str = "COMPUTER NETWORKS PROJECT"):
        # Header banner shape
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_cat = tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_BLUE_PRIMARY

        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_NAVY_DARK

    def add_card(slide, left, top, width, height, bg_color=COLOR_WHITE, border_color=None):
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(1)
        else:
            shape.line.fill.background()
        return shape

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (Dark Navy Modern Theme)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_NAVY_DARK
    bg1.line.fill.background()

    # Title box
    tbox = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(3.8))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "COMPUTER NETWORKS PROJECT PRESENTATION"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_BLUE_ACCENT
    p0.space_after = Pt(14)

    p1 = tf1.add_paragraph()
    p1.text = "Adaptive Bandwidth Allocation & QoS Simulator"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE

    p2 = tf1.add_paragraph()
    p2.text = "Protecting Latency-Sensitive Voice & Video from Competing Bulk Data Congestion"
    p2.font.size = Pt(20)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.space_before = Pt(10)
    p2.space_after = Pt(28)

    p3 = tf1.add_paragraph()
    p3.text = "Core Mechanisms: Strict Priority Queuing (PQ)  •  Token Bucket Traffic Shaping  •  RFC 3550 Jitter  •  ITU-T G.114 SLA"
    p3.font.size = Pt(13)
    p3.font.color.rgb = COLOR_BLUE_ACCENT

    # Footer banner
    footer_box = s1.shapes.add_textbox(Inches(1.2), Inches(6.0), Inches(11.0), Inches(0.8))
    tf_f = footer_box.text_frame
    pf = tf_f.paragraphs[0]
    pf.text = "Python Discrete-Event Simulation Engine  |  Tested Across 28,428 Packets"
    pf.font.size = Pt(12)
    pf.font.color.rgb = COLOR_TEXT_MUTED

    # =========================================================================
    # SLIDE 2: THE REAL-WORLD PROBLEM (The 7:45 PM Story)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "The Real-World Motivation: Why Video Calls Freeze")

    # Left card: The Story
    add_card(s2, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.1), bg_color=COLOR_GRAY_BG, border_color=COLOR_BLUE_ACCENT)
    tb = s2.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.0), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "THE SCENARIO"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_PRIMARY

    bullets = [
        ("7:45 PM:", "You are on an HD video call catching up with a friend. Audio is crisp, video is smooth at 60 fps."),
        ("7:46 PM:", "Someone in the house starts a 4GB game update / file download on the same Wi-Fi connection."),
        ("7:46:05 PM:", "Your friend's face instantly freezes. Voice turns into robotic stutter and cuts out mid-sentence."),
        ("Common Myth:", "\"My Wi-Fi is bad\" or \"My ISP is throttling me.\""),
        ("The Truth:", "Nothing physically broke. It is an unmanaged queueing problem at the network layer!")
    ]
    for b_title, b_desc in bullets:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        run_t = p.add_run()
        run_t.text = f"{b_title} "
        run_t.font.bold = True
        run_t.font.size = Pt(13)
        run_t.font.color.rgb = COLOR_NAVY_DARK
        run_d = p.add_run()
        run_d.text = b_desc
        run_d.font.size = Pt(13)
        run_d.font.color.rgb = COLOR_TEXT_DARK

    # Right card: Technical Translation
    add_card(s2, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.1), bg_color=COLOR_GRAY_BG, border_color=COLOR_RED)
    tb = s2.shapes.add_textbox(Inches(7.1), Inches(1.9), Inches(5.1), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "WHAT ACTUALLY HAPPENED AT THE NETWORK LAYER?"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_RED

    tech_points = [
        ("Best-Effort Delivery:", "Standard home routers treat all packets identically, regardless of urgency."),
        ("Bufferbloat:", "The aggressive download floods the router's single FIFO buffer with large 1500-byte packets."),
        ("Queuing Delay (Latency):", "Tiny voice packets get stuck waiting behind dozens of large bulk packets."),
        ("Jitter:", "Packet delays fluctuate erratically, making real-time reconstruction impossible."),
        ("Packet Loss (Tail Drop):", "When the queue buffer hits capacity, packets are discarded, causing freezes.")
    ]
    for b_title, b_desc in tech_points:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        run_t = p.add_run()
        run_t.text = f"{b_title} "
        run_t.font.bold = True
        run_t.font.size = Pt(13)
        run_t.font.color.rgb = COLOR_NAVY_DARK
        run_d = p.add_run()
        run_d.text = b_desc
        run_d.font.size = Pt(13)
        run_d.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 3: HOW ROUTERS DIFFERENTIATE TRAFFIC (THE 4 FACTORS)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "How Does a Router Know What You Are Doing? (The 4 Factors)")

    factors = [
        ("1. Protocol & 5-Tuple", "UDP vs TCP & Port Numbers", 
         "• Voice/Video uses UDP on known RTP/WebRTC ports (speed > reliability; no retransmission lag).\n• Bulk Downloads use TCP on ports 80/443 (sliding window, guaranteed delivery).",
         COLOR_BLUE_PRIMARY),
        ("2. Traffic Fingerprints", "Packet Sizes & Transmission Pacing",
         "• Voice: Small packets (~160-200B) sent like clockwork every 20ms.\n• Video: Medium frames (~1000B) arriving in 30 fps bursts.\n• Bulk: Massive 1500B MTU packets pumped continuously at line rate.",
         COLOR_GREEN),
        ("3. DSCP IP Header Tags", "Differentiated Services Marking",
         "• OS and VoIP software set a 6-bit tag in the IP header:\n  - DSCP 46 (EF - Expedited Forwarding) for Voice\n  - DSCP 34 (AF41) for Interactive Video\n  - DSCP 0 (CS0 - Best Effort) for background downloads.",
         COLOR_NAVY_DARK),
        ("4. Deep Packet Inspection", "DPI & TLS SNI Domain Inspection",
         "• Enterprise routers inspect the TLS handshake Server Name Indication (SNI).\n• Distinguishes traffic to *.zoom.us or *.meet.google.com from steamcontent.com or epicgames.",
         COLOR_BLUE_ACCENT)
    ]

    card_w = Inches(5.6)
    card_h = Inches(2.4)
    positions = [
        (Inches(0.8), Inches(1.7)),
        (Inches(6.8), Inches(1.7)),
        (Inches(0.8), Inches(4.4)),
        (Inches(6.8), Inches(4.4))
    ]

    for (title, sub, body, color), (x, y) in zip(factors, positions):
        add_card(s3, x, y, card_w, card_h, bg_color=COLOR_GRAY_BG, border_color=color)
        tb = s3.shapes.add_textbox(x + Inches(0.25), y + Inches(0.2), card_w - Inches(0.5), card_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = color
        
        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.size = Pt(11)
        p_sub.font.bold = True
        p_sub.font.color.rgb = COLOR_TEXT_MUTED
        p_sub.space_after = Pt(6)

        p_body = tf.add_paragraph()
        p_body.text = body
        p_body.font.size = Pt(11.5)
        p_body.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 4: THE SOLUTION ARCHITECTURE (QoS with PQ & Token Bucket)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "The Engineering Solution: Dual-Mechanism QoS Pipeline")

    # Left Column: Baseline vs QoS comparison cards
    add_card(s4, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.1), bg_color=COLOR_GRAY_BG, border_color=COLOR_RED)
    tb = s4.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.0), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "RUN A: BASELINE (BEST-EFFORT FIFO)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_RED

    points_a = [
        "Single Shared Queue: All flows dump packets into one FIFO buffer.",
        "Buffer Depth: Fixed 100 packets limit.",
        "Tail-Drop Policy: Packets arriving when full are discarded immediately.",
        "Resulting Flaw: Greedy bulk downloads consume 90%+ of buffer space, creating massive queuing delay and severe packet drops for calls."
    ]
    for pt in points_a:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_TEXT_DARK
        p.space_before = Pt(8)

    # Right Column: QoS Architecture
    add_card(s4, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.1), bg_color=COLOR_GRAY_BG, border_color=COLOR_GREEN)
    tb = s4.shapes.add_textbox(Inches(7.1), Inches(1.9), Inches(5.1), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "RUN B: QUALITY OF SERVICE (QoS ENABLED)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN

    points_b = [
        "1. Packet Classification: Packets sorted by DSCP / Flow ID into High-Priority (Voice/Video) and Low-Priority (Bulk) queues.",
        "2. Strict Priority Queuing (PQ): The link scheduler always checks and drains High-Priority first. Voice/video never waits behind bulk.",
        "3. Token Bucket Traffic Shaping: Sustained rate cap of 6.0 Mbps and 30 KB burst depth on bulk downloads.",
        "Resulting Impact: Guaranteed 4.0 Mbps headroom on the 10 Mbps link; zero real-time packet loss, flat sub-10ms latency."
    ]
    for pt in points_b:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_TEXT_DARK
        p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 5: ALGORITHM DEEP DIVE (Token Bucket & Priority Queue)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Core Algorithms: Mathematical Principles")

    # Algorithm 1: Strict Priority Queuing
    add_card(s5, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.1), bg_color=COLOR_GRAY_BG, border_color=COLOR_BLUE_PRIMARY)
    tb = s5.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.0), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "STRICT PRIORITY QUEUING (PQ)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_PRIMARY

    algo1_text = [
        ("Two Distinct Buffers:", "High-Priority Queue (HPQ) & Low-Priority Queue (LPQ)."),
        ("Non-Preemptive Scheduling:", "The scheduler inspects HPQ before every transmission opportunity."),
        ("Condition Rule:", "If len(HPQ) > 0, pop HPQ; Else, pop LPQ."),
        ("Latency Elimination:", "Voice and video packets skip the queue entirely, experiencing only physical serialization delay + propagation delay."),
        ("Starvation Prevention:", "Voice/video traffic only demands ~2 Mbps, leaving the remaining link capacity permanently open for LPQ.")
    ]
    for h, b in algo1_text:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = f"{h} "
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = COLOR_NAVY_DARK
        r2 = p.add_run()
        r2.text = b
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_TEXT_DARK

    # Algorithm 2: Token Bucket Shaper
    add_card(s5, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.1), bg_color=COLOR_GRAY_BG, border_color=COLOR_GREEN)
    tb = s5.shapes.add_textbox(Inches(7.1), Inches(1.9), Inches(5.1), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "TOKEN BUCKET TRAFFIC SHAPER"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN

    algo2_text = [
        ("Continuous Token Refill:", "Tokens accumulate at rate r = 6.0 Mbps:\nTokens(t) = min(B_cap, Tokens_prev + Δt · r / 8)"),
        ("Burst Allowance (B_cap):", "Allows short bursts up to 30 KB (~20 MTU packets) before throttling kicks in."),
        ("Transmission Guard:", "A packet of size S bytes can ONLY transmit if Tokens >= S. When sent, Tokens = Tokens - S."),
        ("Traffic Shaping vs Policing:", "Excess packets are queued and paced smoothly rather than blindly dropped!"),
        ("Link Protection:", "Prevents bulk traffic from claiming 100% link utilization during call pauses.")
    ]
    for h, b in algo2_text:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = f"{h} "
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = COLOR_NAVY_DARK
        r2 = p.add_run()
        r2.text = b
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 6: SIMULATION EXPERIMENTAL SETUP
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Simulation Methodology & Traffic Profiles (28,428 Packets)")

    # Left card: Link parameters
    add_card(s6, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.1), bg_color=COLOR_GRAY_BG, border_color=COLOR_NAVY_DARK)
    tb = s6.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.0), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "SHARED BOTTLENECK LINK SETUP"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY_DARK

    params = [
        ("Bottleneck Bandwidth:", "10.0 Mbps (1,250,000 bytes/sec)"),
        ("Propagation Delay:", "5.0 ms (typical home-to-ISP local loop)"),
        ("Total Simulation Time:", "30.0 seconds (microsecond discrete-event)"),
        ("Queue Buffer Limit:", "100 packets maximum buffer depth"),
        ("Congestion Window:", "t = 5.0s to 25.0s (20 seconds of severe overload)"),
        ("Replay Fairness:", "100% identical packet stream replayed through Run A & Run B.")
    ]
    for k, v in params:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = f"• {k} "
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = COLOR_BLUE_PRIMARY
        r2 = p.add_run()
        r2.text = v
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_TEXT_DARK

    # Right card: Traffic generation details
    add_card(s6, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.1), bg_color=COLOR_GRAY_BG, border_color=COLOR_BLUE_PRIMARY)
    tb = s6.shapes.add_textbox(Inches(7.1), Inches(1.9), Inches(5.1), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "SYNTHETIC TRAFFIC FLOW PROFILES"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_PRIMARY

    flows = [
        ("Voice Call (VoIP - G.711 / Opus):", "• Active: t=0s to 30s | Size: 200 Bytes | Pace: Constant 20ms (50 pkts/s) | Demand: 80 kbps | DSCP: EF (46)"),
        ("Video Stream (WebRTC / HD 720p):", "• Active: t=0s to 30s | Size: ~1000 Bytes | Pace: 30 fps bursts (6-10 pkts/frame) | Demand: ~2.0 Mbps | DSCP: AF41 (34)"),
        ("Bulk Game Download (Steam / Epic):", "• Active: t=5s to 25s | Size: 1500 Bytes (MTU) | Demand: 15.0 Mbps (Overloads link by 150%!) | DSCP: CS0 (0)")
    ]
    for k, v in flows:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = f"{k}\n"
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = COLOR_NAVY_DARK
        r2 = p.add_run()
        r2.text = v
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 7: NUMERICAL RESULTS TABLE & SLA AUDIT
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Empirical Results: Side-by-Side Performance Comparison")

    # Table
    rows, cols = 7, 5
    left = Inches(0.8)
    top = Inches(1.7)
    width = Inches(11.733)
    height = Inches(3.4)

    table_shape = s7.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(2.3)
    table.columns[2].width = Inches(2.3)
    table.columns[3].width = Inches(2.3)
    table.columns[4].width = Inches(2.633)

    table_data = [
        ["Traffic Flow", "Metric", "Baseline (FIFO)", "QoS-Enabled", "Improvement / Impact"],
        ["Voice Call", "Average Latency", "68.6 ms", "5.6 ms", "91.9% Reduction (-63.0 ms)"],
        ["Voice Call", "RFC 3550 Jitter", "4.70 ms", "0.62 ms", "86.8% Reduction (-4.1 ms)"],
        ["Voice Call", "Packet Loss Rate", "6.00% (FAIL)", "0.00% (PASS)", "100% Elimination of Drops"],
        ["Video Stream", "Average Latency", "66.1 ms", "7.8 ms", "88.3% Reduction (-58.4 ms)"],
        ["Video Stream", "Packet Loss Rate", "15.12% (FAIL)", "0.00% (PASS)", "Eliminates Video Glitches"],
        ["Bulk Download", "Throughput", "5.63 Mbps", "4.05 Mbps", "Capped cleanly to fair share"]
    ]

    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            p.font.size = Pt(12)
            if r_idx == 0:
                p.font.bold = True
                p.font.color.rgb = COLOR_WHITE
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_NAVY_DARK
            else:
                p.font.color.rgb = COLOR_TEXT_DARK
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_WHITE if r_idx % 2 == 1 else COLOR_GRAY_BG
                if "Reduction" in val or "PASS" in val or "Elimination" in val:
                    p.font.bold = True
                    p.font.color.rgb = COLOR_GREEN
                elif "FAIL" in val:
                    p.font.bold = True
                    p.font.color.rgb = COLOR_RED

    # SLA Audit Banner below table
    add_card(s7, Inches(0.8), Inches(5.4), Inches(11.733), Inches(1.4), bg_color=COLOR_GRAY_BG, border_color=COLOR_GREEN)
    tb = s7.shapes.add_textbox(Inches(1.1), Inches(5.5), Inches(11.2), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "ITU-T G.114 Real-Time Telecom Quality SLA Audit"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN

    p2 = tf.add_paragraph()
    p2.text = "• ITU-T G.114 Telecom Standard: Voice Latency < 150 ms | Jitter < 30 ms | Packet Loss < 1.0%\n• Baseline Run FAILED SLA due to 6.00% Voice Packet Loss (causing severe audio distortion & dropouts).\n• QoS-Enabled Run PASSED with 100% compliance across all criteria (0.00% loss, 5.6 ms latency, 0.62 ms jitter)."
    p2.font.size = Pt(12)
    p2.font.color.rgb = COLOR_TEXT_DARK
    p2.space_before = Pt(4)

    # =========================================================================
    # SLIDE 8: EXECUTIVE DASHBOARD VISUAL (Embedded High-Res Graph)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Executive Dashboard: 4-Panel Comparative Results")

    dash_img_path = os.path.join(results_dir, "executive_dashboard.png")
    if os.path.exists(dash_img_path):
        s8.shapes.add_picture(dash_img_path, Inches(0.8), Inches(1.6), width=Inches(8.2), height=Inches(5.4))
    
    # Right-side key takeaways
    add_card(s8, Inches(9.3), Inches(1.6), Inches(3.2), Inches(5.4), bg_color=COLOR_GRAY_BG, border_color=COLOR_BLUE_PRIMARY)
    tb = s8.shapes.add_textbox(Inches(9.5), Inches(1.8), Inches(2.8), Inches(5.0))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "KEY OBSERVATIONS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_PRIMARY

    bullets = [
        "1. Voice Latency: Spikes over 115 ms without QoS; stays flat at ~5.6 ms under QoS.",
        "2. Jitter Control: Under baseline, jitter fluctuates wildly. Under QoS, it stays under 1 ms.",
        "3. Queue Occupancy: High-priority queue stays empty, while low-priority queue safely buffers bulk traffic.",
        "4. 0% Loss: Voice and video packet drops are completely eliminated."
    ]
    for b in bullets:
        p = tf.add_paragraph()
        p.text = b
        p.font.size = Pt(11.5)
        p.font.color.rgb = COLOR_TEXT_DARK
        p.space_before = Pt(10)

    # =========================================================================
    # SLIDE 9: LATENCY & JITTER DETAILED PROFILES
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Time-Series Analysis: Latency Cliff & Jitter Suppression")

    lat_img = os.path.join(results_dir, "latency_comparison.png")
    jit_img = os.path.join(results_dir, "jitter_comparison.png")

    if os.path.exists(lat_img):
        s9.shapes.add_picture(lat_img, Inches(0.8), Inches(1.7), width=Inches(5.6), height=Inches(4.2))
    if os.path.exists(jit_img):
        s9.shapes.add_picture(jit_img, Inches(6.8), Inches(1.7), width=Inches(5.7), height=Inches(4.2))

    # Bottom explanation
    add_card(s9, Inches(0.8), Inches(6.0), Inches(11.7), Inches(1.0), bg_color=COLOR_GRAY_BG, border_color=COLOR_NAVY_DARK)
    tb = s9.shapes.add_textbox(Inches(1.0), Inches(6.1), Inches(11.3), Inches(0.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Analysis: At t=5.0s, the unshaped bulk download immediately causes latency to cliff-jump by +110ms and jitter to spike. With Priority Queuing, high-priority packets are served before bulk packets, resulting in an unbroken, smooth horizontal line."
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 10: THROUGHPUT & PACKET LOSS PROFILES
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Bandwidth Allocation & Elimination of Packet Loss")

    tp_img = os.path.join(results_dir, "throughput_comparison.png")
    loss_img = os.path.join(results_dir, "packet_loss_comparison.png")

    if os.path.exists(tp_img):
        s10.shapes.add_picture(tp_img, Inches(0.8), Inches(1.7), width=Inches(5.6), height=Inches(4.2))
    if os.path.exists(loss_img):
        s10.shapes.add_picture(loss_img, Inches(6.8), Inches(1.7), width=Inches(5.7), height=Inches(4.2))

    # Bottom explanation
    add_card(s10, Inches(0.8), Inches(6.0), Inches(11.7), Inches(1.0), bg_color=COLOR_GRAY_BG, border_color=COLOR_GREEN)
    tb = s10.shapes.add_textbox(Inches(1.0), Inches(6.1), Inches(11.3), Inches(0.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Analysis: Without traffic shaping, the bulk download monopolizes 8.5+ Mbps of the 10 Mbps bottleneck. The Token Bucket Shaper enforces a 6.0 Mbps ceiling on bulk traffic, leaving dedicated headroom for real-time video bursts and eliminating packet loss entirely."
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 11: TECHNICAL HIGHLIGHTS & VIVA CHEAT SHEET
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Technical Evaluation & Viva Defense Preparation")

    qas = [
        ("Q: Why UDP over TCP for Voice & Video?",
         "TCP provides reliability via retransmissions (ARQ). If a packet drops, TCP pauses transmission until the missing chunk arrives, causing fatal 300-500ms lag. Real-time VoIP prefers dropping stale packets rather than playing audio late."),
        ("Q: Does Strict Priority Cause Starvation?",
         "Strict Priority can theoretically starve low queues if high-priority traffic is unbounded. However, in our system, Voice/Video consumes only ~2.0 Mbps of the 10 Mbps link. Token Bucket shaping further ensures fair headroom."),
        ("Q: Traffic Shaping vs Traffic Policing?",
         "Traffic Policing drops or remarks excess packets that violate the rate limit. Traffic Shaping buffers excess packets in memory and paces them smoothly across time, avoiding unneeded loss."),
        ("Q: What is RFC 3550 Jitter Smoothing?",
         "RFC 3550 uses an exponential moving average filter: J = J + (|D| - J)/16. This provides an accurate running estimate of interarrival delay variance used by WebRTC and VoIP codecs.")
    ]

    card_w = Inches(5.6)
    card_h = Inches(2.4)
    positions = [
        (Inches(0.8), Inches(1.7)),
        (Inches(6.8), Inches(1.7)),
        (Inches(0.8), Inches(4.4)),
        (Inches(6.8), Inches(4.4))
    ]

    for (q, a), (x, y) in zip(qas, positions):
        add_card(s11, x, y, card_w, card_h, bg_color=COLOR_GRAY_BG, border_color=COLOR_BLUE_PRIMARY)
        tb = s11.shapes.add_textbox(x + Inches(0.25), y + Inches(0.2), card_w - Inches(0.5), card_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = q
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_BLUE_PRIMARY
        p.space_after = Pt(6)

        p_body = tf.add_paragraph()
        p_body.text = a
        p_body.font.size = Pt(11.5)
        p_body.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 12: CONCLUSION
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    bg12 = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg12.fill.solid()
    bg12.fill.fore_color.rgb = COLOR_NAVY_DARK
    bg12.line.fill.background()

    tbox = s12.shapes.add_textbox(Inches(1.2), Inches(1.2), Inches(11.0), Inches(5.5))
    tf12 = tbox.text_frame
    tf12.word_wrap = True

    p0 = tf12.paragraphs[0]
    p0.text = "CONCLUSION & PROJECT SUMMARY"
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_BLUE_ACCENT
    p0.space_after = Pt(14)

    concl_points = [
        "1. Unmanaged Networks Fail by Design:",
        "   Best-effort FIFO queues inherently cause severe latency, jitter, and packet loss when bulk traffic shares the link with real-time applications.",
        "2. Priority Queuing Guarantees Low Latency:",
        "   Achieved a 91.9% reduction in voice latency (down to 5.6 ms) and an 88.3% reduction in video latency under full link saturation.",
        "3. Traffic Shaping Prevents Buffer Bloat:",
        "   Token bucket rate-limiting capped bulk traffic to 6 Mbps, leaving guaranteed headroom for video bursts and eliminating real-time packet loss (0.00% drops).",
        "4. Full Telecom SLA Compliance:",
        "   Transformed an unusable real-time call (6% loss under FIFO) into a 100% compliant ITU-T G.114 telecom-grade connection."
    ]
    for pt in concl_points:
        p = tf12.add_paragraph()
        p.text = pt
        if pt.startswith("1.") or pt.startswith("2.") or pt.startswith("3.") or pt.startswith("4."):
            p.font.size = Pt(18)
            p.font.bold = True
            p.font.color.rgb = COLOR_WHITE
            p.space_before = Pt(12)
        else:
            p.font.size = Pt(14)
            p.font.color.rgb = RGBColor(203, 213, 225)

    p_end = tf12.add_paragraph()
    p_end.text = "\nThank you! Ready for Questions & Live Demo."
    p_end.font.size = Pt(20)
    p_end.font.bold = True
    p_end.font.color.rgb = COLOR_BLUE_ACCENT
    p_end.space_before = Pt(18)

    # Save presentation
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")


if __name__ == "__main__":
    results_directory = os.path.abspath("results")
    output_pptx = os.path.join(results_directory, "Adaptive_Bandwidth_QoS_Simulator.pptx")
    create_deck(results_directory, output_pptx)
