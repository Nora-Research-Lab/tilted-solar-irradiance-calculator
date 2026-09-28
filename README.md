![NORA logo](https://i.ibb.co/0VJCC9Gf/IMG-20260114-WA0008.jpg)
 
# Tilted Solar Irradiance Calculator
 
*For renewable energy analysts and solar site assessors: enter location, date/time, panel orientation, and ground albedo to instantly compute the plane-of-array irradiance using a clear-sky model.*
 
[![GitHub](https://img.shields.io/badge/GitHub-Nora--Research--Lab-181717?logo=github)](https://github.com/Nora-Research-Lab) [![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-NoraResearchLab-yellow)](https://huggingface.co/NoraResearchLab) [![LinkedIn](https://img.shields.io/badge/LinkedIn-NORA%20Research%20Lab-0A66C2?logo=linkedin)](https://www.linkedin.com/company/nora-research-lab) [![X](https://img.shields.io/badge/X-@noraresearchlab-000000?logo=x)](https://x.com/noraresearchlab) [![NORA Research Lab](https://img.shields.io/badge/Website-noraresearchlab.site-2ea44f)](https://noraresearchlab.site) [![NORA Earth Intelligence](https://img.shields.io/badge/Platform-noraearth.xyz-2ea44f)](https://noraearth.xyz)
 

## Overview
 
**Industry:** Renewable Energy Site Assessment
 
Inputs: (1) Latitude (decimal degrees, -90 to 90), (2) Date (YYYY-MM-DD), (3) UTC-offset (hours, -12 to 14), (4) Local time (HH:MM, 24-hour), (5) Panel tilt from horizontal (0-90°), (6) Panel azimuth (0-360° where 0°=north, 90°=east, 180°=south, 270°=west), (7) Ground albedo (0-1, typical: grass=0.25, snow=0.8).

Calculation logic (step-by-step):
1. Compute day number n from date.
2. Solar declination: δ = 23.45° * sin(360/365 * (n - 81)).
3. Solar time: local time + (4 min)*(longitude correction optional if longitude provided, else assume local standard meridian). For simplicity, skip longitude correction and use local standard meridian based on UTC offset: LS = 15° * UTC_offset. If user enters longitude, compute time correction if provided. Otherwise assume standard.
4. Hour angle h = (solar_time_hours - 12) * 15°.
5. Solar zenith angle θz: cos(θz) = sin(φ)*sin(δ) + cos(φ)*cos(δ)*cos(h), where φ = latitude.
6. Solar elevation α = 90° - θz.
7. Solar azimuth γs: using standard formula with sign convention, calculate sin(γs) and cos(γs).
8. Clear-sky direct normal irradiance DNI using Hottel's model: DNI = DNI0 * τ, where DNI0 = 1367 * (1 + 0.033*cos(360*n/365)) and τ = a0 + a1*exp(-k/cos(θz)). a0, a1, k depend on altitude and climate type (use default: a0=0.423, a1=0.506, k=0.285 for standard clear sky with 23 km visibility). Clamp if cos(θz) < 0.1.
9. Diffuse horizontal irradiance DHI = 0.5 * DNI0 * (1 - τ) * sin(α) / (1 - 1.4*ln(τ))) — simplified from Hottel's diffuse model? Actually use: DHI = DNI * (0.271 - 0.294*τ) for clear sky? Use standard relationship: Diffuse fraction = 0.3 * (1 - τ) if τ>0.15 else 0.7. Better to use a simple isotropic correlation: DHI = DNI0 * (0.271 - 0.294*τ). Then GHI = DNI * cos(θz) + DHI.
10. Angle of incidence on tilted surface: cos(θ) = cos(θz)*cos(tilt) + sin(θz)*sin(tilt)*cos(γs - azimuth).
11. Direct beam on tilted = DNI * cos(θ).
12. Sky diffuse on tilted = DHI * (1+cos(tilt))/2.
13. Ground-reflected on tilted = GHI * albedo * (1-cos(tilt))/2.
14. Total plane-of-array irradiance (POA) = beam + sky + ground.

Output: Numeric display of solar zenith, solar elevation, solar azimuth, DNI, DHI, GHI, and POA irradiance. Also show a small plot (using matplotlib, embedded in Gradio) of solar position on a sky dome or just the POA value. No file download needed.

UI layout: Two columns. Left column inputs (latitude, date, time, offset, tilt, azimuth, albedo, optional longitude). A 
 
## Run it
 
```bash
docker build -t tilted-solar-irradiance-calculator .
docker run -p 7860:7860 tilted-solar-irradiance-calculator
```
 
Then open http://localhost:7860 in your browser.
 
## About
 
This tool was generated and published automatically by the **NORA Earth Intelligence**
tool factory, an autonomous pipeline maintained by **NORA Research Lab** that turns
one idea per run into a small, working geoscience tool — end to end, with an
LLM writing and Docker-testing the code, and another model generating the
banner above.
 
- Platform: [https://noraearth.xyz](https://noraearth.xyz)
- Parent lab: [https://noraresearchlab.site](https://noraresearchlab.site)
 
Built 2026-09-28.
 
---
 
### Maintainer
 
**NORA Research Lab**
[![GitHub](https://img.shields.io/badge/GitHub-Nora--Research--Lab-181717?logo=github)](https://github.com/Nora-Research-Lab) [![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-NoraResearchLab-yellow)](https://huggingface.co/NoraResearchLab) [![LinkedIn](https://img.shields.io/badge/LinkedIn-NORA%20Research%20Lab-0A66C2?logo=linkedin)](https://www.linkedin.com/company/nora-research-lab) [![X](https://img.shields.io/badge/X-@noraresearchlab-000000?logo=x)](https://x.com/noraresearchlab) [![NORA Research Lab](https://img.shields.io/badge/Website-noraresearchlab.site-2ea44f)](https://noraresearchlab.site) [![NORA Earth Intelligence](https://img.shields.io/badge/Platform-noraearth.xyz-2ea44f)](https://noraearth.xyz)
