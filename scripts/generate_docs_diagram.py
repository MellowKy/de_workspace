from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "04_docs/architecture_diagrams"
OUTPUT_PATH = OUTPUT_DIR / "medallion_lakehouse_architecture.png"

def create_diagram():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(18, 10), dpi=300)
    fig.patch.set_facecolor("#0F172A")  # Slate-900 background
    ax.set_facecolor("#0F172A")
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Title & Subtitle Header
    ax.text(9, 9.5, "Medallion Data Lakehouse Architecture", ha="center", va="center",
            fontsize=22, fontweight="bold", color="#F8FAFC", fontfamily="sans-serif")
    ax.text(9, 9.1, "Zero-JVM, In-Memory Vectorized Engine (Delta Lake • DuckDB • dbt • Dagster • FastAPI • Streamlit)",
            ha="center", va="center", fontsize=12, color="#94A3B8", fontfamily="sans-serif")

    def draw_box(x, y, w, h, title, subtitle, bg_color, border_color, title_color="#F8FAFC"):
        box = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.2,rounding_size=0.15",
            linewidth=2, edgecolor=border_color, facecolor=bg_color
        )
        ax.add_patch(box)
        ax.text(x + w / 2, y + h * 0.65, title, ha="center", va="center",
                fontsize=11, fontweight="bold", color=title_color, fontfamily="sans-serif")
        ax.text(x + w / 2, y + h * 0.32, subtitle, ha="center", va="center",
                fontsize=8.5, color="#E2E8F0", fontfamily="sans-serif")

    # Tier 1: Ingress Boundary Gateway
    draw_box(0.8, 5.2, 2.8, 1.8, "Ingress Gateway", "Pydantic V2 OrderContract\nExtra Fields: FORBID", "#1E293B", "#38BDF8")
    
    # Fault Isolation: Dead-Letter Queue
    draw_box(0.8, 1.8, 2.8, 1.8, "Dead-Letter Queue", "orders_dlq.jsonl\nFault Isolation & Replay", "#450A0A", "#EF4444")

    # Tier 2: Bronze ACID Storage
    draw_box(4.4, 5.2, 2.8, 1.8, "Bronze Delta Lake", "raw_orders_bronze\nNative deltalake (ACID Log)", "#3E2723", "#CD7F32", "#FFCC80")

    # Tier 3: Silver Modeling Tier
    draw_box(8.0, 5.2, 2.8, 1.8, "Silver Staging", "stg_orders (dbt-duckdb)\nDISTINCT ON (event_id)", "#263238", "#C0C0C0", "#ECEFF1")

    # Tier 4: Gold Analytics Mart
    draw_box(11.6, 5.2, 2.8, 1.8, "Gold Data Product", "fct_daily_sales (Delta)\nDaily Sales & Revenue Aggs", "#3E2F00", "#FFD700", "#FFF9C4")

    # Tier 5: Serving Channels
    draw_box(15.2, 6.4, 2.4, 1.4, "FastAPI REST", "Port 8000 | Arrow Zero-Copy\n/api/v1/sales/daily", "#064E3B", "#10B981")
    draw_box(15.2, 4.4, 2.4, 1.4, "Streamlit UI", "Port 8501 | Real-Time KPIs\nDuckDB In-Memory Scans", "#581C87", "#A855F7")

    # Enterprise Control Plane Box: Positional arguments correctly supplied
    control_box = patches.FancyBboxPatch(
        (4.4, 1.2), 10.0, 2.4,
        boxstyle="round,pad=0.2,rounding_size=0.15",
        linewidth=1.5, edgecolor="#64748B", facecolor="#1E293B", linestyle="--"
    )
    ax.add_patch(control_box)
    ax.text(9.4, 3.2, "ENTERPRISE CONTROL & GOVERNANCE PLANE", ha="center", va="center",
            fontsize=10, fontweight="bold", color="#94A3B8", fontfamily="sans-serif")
    
    # Internal Control Nodes
    draw_box(4.8, 1.5, 2.8, 1.3, "Dagster Orchestrator", "Software-Defined Assets\nLifecycle Execution", "#0F172A", "#38BDF8")
    draw_box(8.0, 1.5, 2.8, 1.3, "dbt Test Assertions", "unique, not_null, accepted_values\nDuckDB In-Process Engine", "#0F172A", "#F59E0B")
    draw_box(11.2, 1.5, 2.8, 1.3, "GitHub Actions CI", "ci.yml: ruff + pytest -W error\nUbuntu Isolated Runner", "#0F172A", "#10B981")

    def draw_arrow(x1, y1, x2, y2, color="#94A3B8", label=None, label_y=None):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6",
                            color=color, lw=2, shrinkA=3, shrinkB=3)
        )
        if label:
            ly = label_y if label_y else (y1 + y2) / 2 + 0.25
            ax.text((x1 + x2) / 2, ly, label, ha="center", va="center",
                    fontsize=8, color=color, fontweight="bold", fontfamily="sans-serif")

    # Horizontal Pipeline Data Flow Arrows
    draw_arrow(3.6, 6.1, 4.4, 6.1, color="#38BDF8", label="Valid PyArrow")
    draw_arrow(7.2, 6.1, 8.0, 6.1, color="#CD7F32", label="Delta Log Scan")
    draw_arrow(10.8, 6.1, 11.6, 6.1, color="#C0C0C0", label="dbt Ref")
    
    # Dual Serving Channel Split Arrows
    draw_arrow(14.4, 6.4, 15.2, 7.1, color="#FFD700", label="Arrow Buffer")
    draw_arrow(14.4, 5.8, 15.2, 5.1, color="#FFD700")

    # Ingress to DLQ Error Flow
    draw_arrow(2.2, 5.2, 2.2, 3.6, color="#EF4444", label="ValidationError")

    # DLQ Replayer Remediated Append Flow
    ax.annotate(
        "", xy=(4.4, 5.6), xytext=(3.6, 2.7),
        arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6",
                        color="#F59E0B", lw=2, linestyle="--",
                        connectionstyle="arc3,rad=-0.2")
    )
    ax.text(4.2, 3.8, "Remediated Replay (Commit v1)", ha="center", va="center",
            fontsize=8, color="#F59E0B", fontweight="bold", fontfamily="sans-serif")

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, facecolor=fig.get_facecolor(), edgecolor="none", dpi=300)
    plt.close()
    print(f"Architecture diagram rendered successfully at: {OUTPUT_PATH}")

if __name__ == "__main__":
    create_diagram()
