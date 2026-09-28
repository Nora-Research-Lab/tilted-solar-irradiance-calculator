import math
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def day_number(date_str):
    """Compute day of year from YYYY-MM-DD string (1-366)."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.timetuple().tm_yday

def solar_declination(n):
    """Compute solar declination in degrees."""
    return 23.45 * math.sin(math.radians(360.0/365 * (n - 81)))

def hour_angle(solar_time_hours):
    """Compute hour angle in degrees. solar_time_hours in decimal hours."""
    return (solar_time_hours - 12.0) * 15.0

def solar_time(local_time, utc_offset, longitude=None):
    """
    Convert local time to solar time in decimal hours.
    If longitude is provided, compute time correction; else use local standard meridian.
    local_time: string "HH:MM" 24-hour.
    utc_offset: hours.
    longitude: decimal degrees (optional).
    """
    parts = local_time.split(":")
    local_decimal = int(parts[0]) + int(parts[1])/60.0
    if longitude is None or longitude == "" or longitude == "":
        # Use standard meridian
        standard_meridian = 15.0 * utc_offset
        time_correction = 0.0
    else:
        longitude = float(longitude)
        standard_meridian = 15.0 * utc_offset
        # Equation of time: approximate
        n = None  # We'll need day number, but we don't have it here. We'll approximate with average? Use zero.
        # For simplicity, use the standard meridian correction only.
        time_correction = 4.0 * (standard_meridian - longitude) / 60.0  # in hours
    solar_time_decimal = local_decimal + time_correction
    return solar_time_decimal

def solar_zenith_angle(lat, decl, h):
    """Compute solar zenith angle in degrees."""
    phi = math.radians(lat)
    delta = math.radians(decl)
    cos_theta_z = math.sin(phi)*math.sin(delta) + math.cos(phi)*math.cos(delta)*math.cos(math.radians(h))
    cos_theta_z = max(min(cos_theta_z, 1.0), -1.0)
    theta_z = math.degrees(math.acos(cos_theta_z))
    return theta_z

def solar_elevation(theta_z):
    """Solar elevation in degrees."""
    return 90.0 - theta_z

def solar_azimuth(lat, decl, h, theta_z):
    """
    Compute solar azimuth in degrees from north clockwise.
    """
    phi = math.radians(lat)
    delta = math.radians(decl)
    h_rad = math.radians(h)
    cos_theta_z = math.cos(math.radians(theta_z))
    # Use standard formula
    # Azimuth from north clockwise (0 north, 90 east, 180 south, 270 west)
    # From Duffie & Beckman: azimuth = atan2(sin(h), cos(h)*sin(phi) - tan(delta)*cos(phi)) + 180
    temp = math.sin(h_rad)
    denom = math.cos(h_rad)*math.sin(phi) - math.tan(delta)*math.cos(phi)
    if abs(denom) < 1e-10:
        denom = 1e-10
    azimuth_rad = math.atan2(temp, denom) + math.pi  # in radians, between 0 and 2*pi
    azimuth_deg = math.degrees(azimuth_rad)
    # Ensure 0-360
    azimuth_deg = azimuth_deg % 360.0
    return azimuth_deg

def extraterrestrial_dni(n):
    """Extraterrestrial DNI at day number n (W/m^2)."""
    DNI0 = 1367.0 * (1 + 0.033 * math.cos(math.radians(360.0 * n / 365)))
    return DNI0

def clear_sky_transmittance(theta_z, a0=0.423, a1=0.506, k=0.285):
    """Hottel's clear sky transmittance for beam irradiance. theta_z in degrees."""
    cos_theta_z = math.cos(math.radians(theta_z))
    if cos_theta_z < 0.1:
        cos_theta_z = 0.1
    tau = a0 + a1 * math.exp(-k / cos_theta_z)
    return tau

def compute_poa(lat, date_str, utc_offset, local_time, tilt_deg, azimuth_deg, albedo, longitude=None):
    """
    Main function to compute POA irradiance.
    Returns dict with keys: solar_zenith, solar_elevation, solar_azimuth, dni, dhi, ghi, poa.
    Returns None if sun is below horizon (zenith > 90).
    """
    try:
        tilt = math.radians(tilt_deg)
        az = math.radians(azimuth_deg)
        n = day_number(date_str)
        decl = solar_declination(n)
        solar_time_decimal = solar_time(local_time, utc_offset, longitude)
        h = hour_angle(solar_time_decimal)
        theta_z = solar_zenith_angle(lat, decl, h)
        if theta_z >= 90.0:
            return None  # Sun below horizon
        elevation = solar_elevation(theta_z)
        gamma_s = solar_azimuth(lat, decl, h, theta_z)
        DNI0 = extraterrestrial_dni(n)
        tau = clear_sky_transmittance(theta_z)
        DNI = DNI0 * tau
        # DHI from standard correlation (clear-sky)
        DHI = DNI0 * (0.271 - 0.294 * tau)
        if DHI < 0:
            DHI = 0.0
        GHI = DNI * math.cos(math.radians(theta_z)) + DHI
        # Angle of incidence on tilted surface
        cos_theta = math.cos(math.radians(theta_z)) * math.cos(tilt) + \
                    math.sin(math.radians(theta_z)) * math.sin(tilt) * math.cos(math.radians(gamma_s - azimuth_deg))
        cos_theta = max(cos_theta, 0.0)
        beam_tilt = DNI * cos_theta
        sky_diffuse = DHI * (1 + math.cos(tilt)) / 2.0
        ground_reflected = GHI * albedo * (1 - math.cos(tilt)) / 2.0
        POA = beam_tilt + sky_diffuse + ground_reflected
        return {
            "solar_zenith": theta_z,
            "solar_elevation": elevation,
            "solar_azimuth": gamma_s,
            "dni": DNI,
            "dhi": DHI,
            "ghi": GHI,
            "poa": POA
        }
    except Exception as e:
        # Return None on error
        return None

def plot_sky_dome(azimuth_deg, elevation_deg):
    """
    Generate a polar plot of sun position on the sky dome.
    Azimuth from north clockwise (angle in polar coordinates), elevation as radial distance.
    Returns matplotlib figure.
    """
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={'projection': 'polar'})
    # Convert azimuth: polar plot uses angle from east in mathematical direction. Standard: angle=0 is east, counter-clockwise.
    # We have azimuth from north clockwise. To map: polar angle = (90 - azimuth) in degrees? Actually 0 in polar = right (east), 90 = north.
    # So polar angle (radians) = (90 - azimuth_deg) * pi/180. Or we can convert by rotating.
    # Simpler: Use custom projection? We'll just convert to radians.
    azimuth_rad = math.radians(90 - azimuth_deg)  # because 0 east, 90 north
    # Elevation: from horizon (0) to zenith (90). Radial coordinate: use 90 - elevation as radius (so zenith at center).
    radius = 90 - elevation_deg
    ax.scatter(azimuth_rad, radius, color='orange', s=100, label='Sun position')
    # Draw horizon circle
    ax.set_ylim(0, 90)
    ax.set_yticks([15, 30, 45, 60, 75])
    ax.set_yticklabels(['75°', '60°', '45°', '30°', '15°'])
    ax.set_theta_zero_location("N")  # Sets 0° at North
    ax.set_theta_direction(-1)  # Clockwise increase
    ax.set_title("Sky Dome (Sun Position)", va='bottom')
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    fig.tight_layout()
    return fig
