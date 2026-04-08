# <img src="https://userinsights.signsbeat.com/favicon.ico" width="28" height="28" alt=""> Yishii by Signsbeat for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License](https://img.shields.io/badge/License-Proprietary-blue.svg)](#license)
[![HA Version](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-brightgreen.svg)](https://www.home-assistant.io)
[![GitHub release|202](https://img.shields.io/github/release/vupham79/ha-integration-signsbeat.svg)https://github.com/Retech-Asia/official-signsbeat-homeassistant](https://github.com/Retech-Asia/official-signsbeat-homeassistant)

**Official Home Assistant integration for Yishii** — a sleep and recovery intelligence platform that bridges wearable biometrics and smart home data. This integration pulls your Yishii Health Score into Home Assistant, enabling your home environment to respond intelligently to your physiological state.

> 🟢 **Recovery** · 🟠 **Mild Stress** · 🔴 **Stress** — your home now knows the difference.

---

## What is Signsbeat?

Signsbeat, the company behind the Longevity and lifestyle application Yishii which is a wellness intelligence platform that synthesises data from wearables (Apple Watch, Garmin, Signsbeat Partner device and more), environmental sensors (temperature, humidity, CO₂, ambient noise), dietary logs, and Apple HealthKit / Android Health Connect to produce a **proprietary, inflammation-informed metric. Unlike generic readiness metrics, Yishii's score is grounded in biomarker analysis that is science based giving you a scientific meaningful idea of where your body state is today.

This Home Assistant integration brings that score directly into your smart home ecosystem, so your home can act on your biology and not just your schedule.

---

## Features

- **Proprietary Health Score** — Yishii's inflammation-based daily score exposed as a native HA sensor
- **Three-State Health Classification** — `Recovery`, `Mild Stress`, and `Stress` states available as text sensors for automation logic
- **Score Date Tracking** — know exactly when your latest score was computed
- **Static API Key Auth** — simple, secure token-based authentication with no OAuth redirect complexity
- **Configurable Polling** — pull-based update interval tunable to your preference
- **HACS Compatible** — one-click install and update via HACS
- **Lovelace-Ready** — full suite of YAML card examples included, from gauges to the Yishii Sanctuary custom card
- **Automation-First Design** — built for the HA power user who wants their home to react to health state in real time

---

## Available Sensors

| Entity | Entity ID | Description | Unit |
|--------|-----------|-------------|------|
| Health Score | `sensor.signsbeat_health_score` | Daily inflammation-based health score | `0–100` |
| Health Status | `sensor.signsbeat_health_status` | Classified state: `Recovery`, `Mild Stress`, or `Stress` | `string` |
| Score Date | `sensor.signsbeat_score_date` | Date the current score was computed by Signsbeat | `date` |

### Health Status Reference

| State          | Value         | Colour           | Interpretation                                                                                                         |
| -------------- | ------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------- |
| 🟢 Recovery    | `Recovery`    | Green `#4CAF50`  | Your body has recovered well. High readiness for training, cognitive work, or social demands.                          |
| 🟠 Mild Stress | `Mild Stress` | Orange `#FF9800` | Moderate physiological load detected. Proceed with intention to avoid pushing hard today.                              |
| 🔴 Stress      | `Stress`      | Red `#F44336`    | Elevated stress markers detected. Prioritise rest, hydration, and low-stimulation environments. Wind down and recover. |

> **Note:** Scores are computed nightly by Yishii after your wearable syncs your sleep data. All three sensors update once per day after sync completes. Check `sensor.signsbeat_score_date` to confirm you are viewing today's score.

---

## Requirements

- **Home Assistant** 2024.1 or later (recommended)
- **HACS** installed ([install guide](https://hacs.xyz/docs/use/download/download/))
- An active **Yishii account** with an active Personal Access Token ([get one here](https://userinsights.signsbeat.com/en/dashboard))

---

## Installation

### Step 1 — Install via HACS

1. Open **HACS** in your Home Assistant sidebar
2. Click **Integrations**
3. Click the **⋮ menu** (top right) → **Custom repositories**
4. Add the repository URL: `https://github.com/Retech-Asia/official-signsbeat-homeassistant`
5. Set category to **Integration** → click **Add**
6. Search for **Signsbeat** → click **Download**
7. **Restart Home Assistant**

### Step 2 — Generate Your Yishii API Key

1. Log in to the Signsbeat web app at [userinsights.signsbeat.com](https://userinsights.signsbeat.com/en/dashboard)
2. In the **left sidebar**, click **Settings**
3. Under **Account Settings**, click **Personal Access Token**
4. Click **+ Generate Token**
5. Give it a label (e.g. `Home Assistant`)
6. **Copy the token string** — you will not be able to view it again after leaving the page
7. Confirm the token status shows **Active** ✅

### Step 3 — Add the Integration to Home Assistant

1. Go to **Settings → Devices & Services**
2. Click **+ Add Integration**
3. Search for **Signsbeat**
4. Paste your **API Key** into the configuration field
5. Click **Submit**

Your Signsbeat sensors will appear immediately under the Signsbeat integration entry.

---

## Dashboard Examples

### 1. Recovery Score Gauge

A quick-glance visual with colour-coded severity bands.

```yaml
type: gauge
entity: sensor.signsbeat_health_score
name: Health Score
needle: true
min: 0
max: 100
severity:
  green: 70
  yellow: 40
  red: 0
```

---

### 2. Health Score Trend — 7-Day ApexCharts

Track your score trajectory over the past week to spot patterns in your recovery cycle.

> Requires [apexcharts-card](https://github.com/RomRider/apexcharts-card) via HACS.

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Signsbeat Health Score Trend
  show_states: true
  colorize_states: true
graph_span: 7d
span:
  end: day
series:
  - entity: sensor.signsbeat_health_score
    name: Health Score
    color: "#0098C0"
    stroke_width: 3
    type: line
    curve: smooth
    group_by:
      func: last
      duration: 1d
yaxis:
  - min: 0
    max: 100
    apex_config:
      tickAmount: 5
      title:
        text: Score
```

---

### 3. Entities Summary Card

A clean daily summary of all three Signsbeat sensors. The Health Status row uses a `mushroom-template-card` so the icon colour dynamically reflects your current state — green for Recovery, orange for Mild Stress, red for Stress.

> Requires [mushroom-cards](https://github.com/piitaya/lovelace-mushroom) via HACS.

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Signsbeat — Today
    entities:
      - entity: sensor.signsbeat_health_score
        name: Health Score
        secondary_info: last-changed
        icon: mdi:heart-pulse
      - entity: sensor.signsbeat_score_date
        name: Score Date
        icon: mdi:calendar-today
        secondary_info: false
  - type: custom:mushroom-template-card
    primary: Health Status
    secondary: "{{ states('sensor.signsbeat_health_status') }}"
    entity: sensor.signsbeat_health_status
    icon: mdi:circle
    icon_color: >
      {% if is_state('sensor.signsbeat_health_status', 'Recovery') %}green
      {% elif is_state('sensor.signsbeat_health_status', 'Mild Stress') %}orange
      {% else %}red{% endif %}
    layout: horizontal
    fill_container: true
```

> **Why the split layout?** Standard `entities` card rows do not support templated icon colours — that capability lives in `mushroom-template-card`. The status row is placed beneath as a mushroom card, giving you full colour reactivity while keeping the score and date in the clean native HA style.

---

### 4. Mushroom Status Card with Colour-Coded State

A standalone status card with a dynamically coloured icon and score-based emoji badge. Drop this on your main dashboard for an at-a-glance morning read.

> Requires [mushroom-cards](https://github.com/piitaya/lovelace-mushroom) via HACS.

```yaml
type: custom:mushroom-template-card
primary: Signsbeat Health
secondary: "{{ states('sensor.signsbeat_health_status') }}"
entity: sensor.signsbeat_health_status
icon: mdi:heart-pulse
icon_color: >
  {% if is_state('sensor.signsbeat_health_status', 'Recovery') %}green
  {% elif is_state('sensor.signsbeat_health_status', 'Mild Stress') %}orange
  {% else %}red{% endif %}
badge_icon: >
  {% set score = states('sensor.signsbeat_health_score') | int(0) %}
  {% if score >= 70 %}mdi:emoticon-happy
  {% elif score >= 40 %}mdi:emoticon-neutral
  {% else %}mdi:emoticon-sad{% endif %}
badge_color: >
  {% set score = states('sensor.signsbeat_health_score') | int(0) %}
  {% if score >= 70 %}green
  {% elif score >= 40 %}orange
  {% else %}red{% endif %}
```

> **Debugging tips for this card:**
> - Always use `is_state('sensor.signsbeat_health_status', 'Recovery')` rather than `states(...) == 'Recovery'` — it handles whitespace and edge cases more reliably.
> - Use `| int(0)` (not `| int`) when casting the score — this prevents template errors when the sensor value is `unavailable` or `unknown` during HA startup.
> - To verify the exact live value your integration returns, open **Developer Tools → Template** and run: `{{ states('sensor.signsbeat_health_status') }}`. The result must match `Recovery`, `Mild Stress`, or `Stress` exactly, including capitalisation.

---

### 5. Signsbeat Sanctuary Card

The full branded Signsbeat Sanctuary custom card, themed to Signsbeat's visual identity (`#002838` background, `#0098C0` primary, `#38C8F8` accent).

> Requires the `signsbeat-sanctuary-card` Lovelace frontend resource installed via HACS.

```yaml
type: custom:signsbeat-sanctuary-card
entities:
  health_score: sensor.signsbeat_health_score
  health_status: sensor.signsbeat_health_status
  score_date: sensor.signsbeat_score_date
title: Sanctuary
theme: signsbeat
```

---

## Automation Examples

### 1. Morning Health Briefing (TTS)

Announces your health score and personalised state guidance each morning via any TTS-compatible speaker (WiiM, Google Home, Sonos, etc.).

```yaml
automation:
  - alias: "Signsbeat — Morning Health Briefing"
    description: "Announce health score and status each morning after wearable sync"
    trigger:
      - platform: time
        at: "07:30:00"
    condition:
      - condition: not
        conditions:
          - condition: state
            entity_id: sensor.signsbeat_health_status
            state: "unavailable"
          - condition: state
            entity_id: sensor.signsbeat_health_status
            state: "unknown"
    action:
      - service: tts.speak
        target:
          entity_id: media_player.bedroom_speaker   # replace with your speaker entity
        data:
          message: >
            Good morning. Your Signsbeat health score today is
            {{ states('sensor.signsbeat_health_score') }} out of 100,
            scored on {{ states('sensor.signsbeat_score_date') }}.
            Your status is {{ states('sensor.signsbeat_health_status') }}.
            {% if is_state('sensor.signsbeat_health_status', 'Recovery') %}
              You are well recovered. Your body is ready — make the most of today.
            {% elif is_state('sensor.signsbeat_health_status', 'Mild Stress') %}
              Mild physiological stress detected. Proceed with intention and avoid pushing hard.
            {% else %}
              Elevated stress detected. Prioritise rest, light movement, and wind-down activities today.
            {% endif %}
```

---

### 2. Morning Ambient Light — Recovery State Colour (Philips Hue / RGB)

Sets your light to your recovery state colour at wake time. A silent, zero-effort visual cue — before you check your phone, your home has already told you how your body is doing.

| Status | Colour | RGB |
|--------|--------|-----|
| Recovery | 🟢 `#4CAF50` | `[76, 175, 80]` |
| Mild Stress | 🟠 `#FF9800` | `[255, 152, 0]` |
| Stress | 🔴 `#F44336` | `[244, 67, 54]` |

```yaml
automation:
  - alias: "Signsbeat — Morning Recovery Light"
    description: "Set ambient light colour based on Signsbeat health status"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: not
        conditions:
          - condition: state
            entity_id: sensor.signsbeat_health_status
            state: "unavailable"
    action:
      - service: light.turn_on
        target:
          entity_id: light.bedroom_hue_ambiance   # replace with your light entity
        data:
          brightness_pct: 60
          rgb_color: >
            {% if is_state('sensor.signsbeat_health_status', 'Recovery') %}
              [76, 175, 80]
            {% elif is_state('sensor.signsbeat_health_status', 'Mild Stress') %}
              [255, 152, 0]
            {% else %}
              [244, 67, 54]
            {% endif %}
          transition: 5
```

> 💡 **Philips Hue users:** Replace `light.bedroom_hue_ambiance` with your Hue entity ID. For Zigbee RGB strips via Zigbee2MQTT, the same `rgb_color` template applies directly. The 5-second `transition` creates a gentle sunrise effect.

---

### 3. Fully Kiosk — Recovery Dashboard Display

Switches your Fully Kiosk Browser tablet to the appropriate Lovelace view when your health status updates, surfacing context-appropriate recommendations for your state.

```yaml
automation:
  - alias: "Signsbeat — Fully Kiosk Recovery Display"
    description: "Load the appropriate Lovelace view on the Fully Kiosk tablet when health status changes"
    trigger:
      - platform: state
        entity_id: sensor.signsbeat_health_status
    condition:
      - condition: not
        conditions:
          - condition: state
            entity_id: sensor.signsbeat_health_status
            state: "unavailable"
    action:
      - service: fully_kiosk.load_url
        target:
          entity_id: media_player.fully_kiosk_tablet   # replace with your Fully Kiosk device entity
        data:
          url: >
            {% if is_state('sensor.signsbeat_health_status', 'Recovery') %}
              http://homeassistant.local:8123/lovelace/recovery
            {% elif is_state('sensor.signsbeat_health_status', 'Mild Stress') %}
              http://homeassistant.local:8123/lovelace/mild-stress
            {% else %}
              http://homeassistant.local:8123/lovelace/stress
            {% endif %}
```

**Recommended Lovelace view structure:**

| Path | Status | Suggested content |
|------|--------|-------------------|
| `/lovelace/recovery` | 🟢 Recovery | Active training plan, productivity focus, high-output recommendations |
| `/lovelace/mild-stress` | 🟠 Mild Stress | Moderate activity suggestions, mindfulness prompts, hydration reminders |
| `/lovelace/stress` | 🔴 Stress | Wind-down content, sleep hygiene tips, breathwork, low-stimulation mode |

---

## Troubleshooting

### Sensors show as `unavailable` after setup

- Confirm your Personal Access Token is **Active** in the Signsbeat dashboard
- Ensure the token was copied in full with no leading or trailing whitespace
- Reconfigure via **Settings → Devices & Services → Signsbeat → Configure**
- Check **Settings → System → Logs** and filter for `signsbeat` to view API errors

### Score has not updated today

- Signsbeat computes scores after overnight wearable sync, typically between 06:00–09:00 local time
- Check `sensor.signsbeat_score_date` — if it shows yesterday's date, the nightly computation has not yet completed
- Verify a score is visible in the Signsbeat web dashboard before expecting HA to reflect it

### Mushroom card icon colour is not changing

- Open **Developer Tools → Template** and run `{{ states('sensor.signsbeat_health_status') }}` to verify the exact string your integration returns
- State values are case-sensitive: `Recovery`, `Mild Stress`, `Stress` — any variation will cause the template to fall through to the `else` (red) branch
- Use `is_state()` rather than `states(...) == '...'` for all health status comparisons
- Use `| int(0)` when casting `sensor.signsbeat_health_score` to avoid errors on `unavailable`

### API authentication errors in logs

- Regenerate a new Personal Access Token in the Signsbeat dashboard
- Reconfigure the integration via **Settings → Devices & Services → Signsbeat → Configure**
- Each HA instance should use its own labelled token for traceability

---

## Entity ID Quick Reference

| Sensor | Entity ID | Example value |
|--------|-----------|---------------|
| Health Score | `sensor.signsbeat_health_score` | `78` |
| Health Status | `sensor.signsbeat_health_status` | `Recovery` |
| Score Date | `sensor.signsbeat_score_date` | `2026-04-07` |

---

## Roadmap

- [ ] Additional biometric sensors (HRV, resting heart rate, sleep stages) as Signsbeat API expands
- [ ] Historical score statistics for HA Long-Term Statistics support
- [ ] Yishii Personalised Recommendation module
- [x] Multi-user / multi-account support

---

## Contributing

This is an official Signsbeat integration. Bug reports, feature requests, and pull requests are welcome via the [Issues](https://github.com/Retech-Asia/official-signsbeat-homeassistant/issues) tab.

Please include your Home Assistant version, integration version, and relevant logs from **Settings → System → Logs** when filing an issue.

---

## Support

If you find this integration helpful, consider supporting its development:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/retechasia)

---

## License

© Signsbeat. All rights reserved.

This integration is provided for personal use by Signsbeat subscribers. Redistribution, modification, or commercial use without explicit written permission from Signsbeat is prohibited.

---

## Disclaimer

This is the official Signsbeat Home Assistant integration, maintained by the Signsbeat team. Signsbeat health data is intended for personal wellness and lifestyle awareness and does not constitute medical advice. Always consult a qualified healthcare professional for clinical decisions.

---

<p align="center">
  <a href="https://userinsights.signsbeat.com">
    <img src="https://img.shields.io/badge/Signsbeat-userinsights.signsbeat.com-0098C0?style=for-the-badge" alt="Signsbeat">
  </a>
</p>
