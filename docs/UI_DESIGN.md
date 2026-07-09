# AutoOps UI/UX Design Specification

This document details the frontend user interface (UI) design systems, layouts, component styles, and interaction guidelines for the **AutoOps** console. The interface is optimized for high data density, readability, and standard enterprise operations.

---

## 1. Design Token System

AutoOps implements a clean, flat, high-density dark mode design system aligned with professional DevOps tools (e.g., Grafana, Datadog, or Tailwind UI). 

### A. Color Palette
- **Base Backgrounds:**
  - `bg-primary`: `#0B0F19` (Main canvas backdrop)
  - `bg-surface`: `#161D2B` (Sidebar, header, and card containers)
  - `bg-element`: `#212C3F` (Input fields, hover states, active menu items)
- **Dividers & Borders:**
  - `border-default`: `#2D394E` (Grid division lines and borders)
  - `border-focus`: `#3B82F6` (Focused inputs and active item highlights)
- **Status Colors (Muted Semantic Tones):**
  - `status-critical (P0/P1)`: Text: `#F87171` | Background: `#451A1A` | Border: `#7F1D1D`
  - `status-warning (P2)`: Text: `#FBBF24` | Background: `#3C240E` | Border: `#78350F`
  - `status-success / resolved`: Text: `#34D399` | Background: `#064E3B` | Border: `#065F46`
  - `status-info / active`: Text: `#60A5FA` | Background: `#1E3A8A` | Border: `#1E40AF`
- **Text Scale:**
  - `text-primary`: `#F3F4F6` (Labels, values, titles)
  - `text-secondary`: `#9CA3AF` (Descriptions, secondary table headers)
  - `text-muted`: `#6B7280` (Timestamps, code comments, system logs)

### B. Typography
- **UI & Controls:** `Inter`, `-apple-system`, `BlinkMacSystemFont`, `sans-serif`
- **Telemetry & Terminal Code:** `SFMono-Regular`, `Consolas`, `Liberation Mono`, `monospace`

---

## 2. Layout & Workspace Grid

The AutoOps console uses a split-screen dashboard to ensure SREs can track root-cause reasoning while inspecting corresponding telemetry:

### A. Sidebar Navigation (Left Column)
- **Width:** `240px` (Fixed)
- **Background:** `bg-surface` with a solid `1px` border-right (`border-default`).
- **Items:** Text links with small SVG icons (Dashboard, Telemetry Config, History, Settings).

### B. Workspace Split Layout
The incident details view uses a clean, two-column split pane:

```text
+------------------------------------------------------------------------------------+
| [Header] P0 Incident: HTTP 502 Bad Gateway in 'frontend-api'                       |
| Triggered: 14:32:01 | Duration: 12m | Status: INVESTIGATING | Owner: --            |
+------------------------------------+-----------------------------------------------+
|                                    |                                               |
|  LEFT PANEL (60% Width)            | RIGHT PANEL (40% Width)                       |
|  Reasoner Node Graph               | Investigation Timeline & SRE Chat             |
|                                    |                                               |
|  [React Flow Canvas]               |  [Triage Timeline Feed]                       |
|  ┌─────────────────────────────┐   |  14:32:05 [Metrics Node]                      |
|  │ Start                       │   |  Queried Prometheus metrics for HTTP rate.    |
|  └──────────────┬──────────────┘   |                                               |
|                 ▼                  |  14:32:12 [Logs Node]                         |
|  ┌─────────────────────────────┐   |  Found connection error in Loki logs.         |
|  │ Metrics: http_requests_err  │   |  Captured trace ID: 4a2b91c0                  |
|  └──────────────┬──────────────┘   |                                               |
|                 ▼                  |  -------------------------------------------  |
|  ┌─────────────────────────────┐   |  [Ad-Hoc Agent Chat]                          |
|  │ Logs: frontend-api errors   │   |  SRE: "Compare DB metrics for the last hour"  |
|  └─────────────────────────────┘   |  AI:  "Here are the DB connection pools..."   |
|                                    |  [Input: Ask follow-up question...]          |
+------------------------------------+-----------------------------------------------+
| BOTTOM PANEL (Full Width - Collapsible)                                            |
| Suggested Remediation: `kubectl rollout undo deployment/frontend-api`              |
| [ Approve and Execute ]                                      [ Copy Command ]      |
+------------------------------------------------------------------------------------+
```

---

## 3. Structured React Flow Node Designs

Instead of flashing lights or complex visuals, nodes are rendered as clean, high-density cards with standardized headers.

1. **Metrics Node:**
   - **Header:** Pill badge `PROMETHEUS`, bold status text.
   - **Body:** Renders a clean line chart (1px border, neutral gray gridlines) showing query output trends over time. PromQL syntax box beneath.
2. **Logs Node:**
   - **Header:** Pill badge `GRAFANA LOKI`.
   - **Body:** High-density raw log table with red indicators highlighting errors.
3. **Traces Node:**
   - **Header:** Pill badge `JAEGER / OPENTELEMETRY`.
   - **Body:** Standard span list showing latency percentage bars relative to total trace duration.
4. **Change Event Node:**
   - **Header:** Pill badge `KUBERNETES / GIT`.
   - **Body:** List of deployment events, Kubernetes status codes, or Git diff shortcodes.

---

## 4. UI Indicators & States

- **Loading / Active Nodes:**
  - Nodes actively querying data display a small, rotating circular spinner next to the node label.
  - Border style shifts from `border-default` to `border-focus` (solid blue). No glow or neon animations.
- **Node Interaction:**
  - Clicking a node highlights it with a blue border and opens a side drawer detailing the query options and parameters.
- **Action Execution:**
  - Remediation buttons state transition: `Idle (Default)` -> `Executing (Disabled + Spinner)` -> `Success (Checkmark)` or `Error (Muted Red)`.
- **Transitions:**
  - Drawers and modals use a standard CSS transition (`transition-all duration-150 ease-out`) for fast and predictable layouts.
