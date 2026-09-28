import gradio as gr
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tilted_solar_irradiance_calculator import compute_poa, plot_sky_dome
import datetime

def validate_non_empty(value, name):
    if value is None or value == "":
        raise ValueError(f"{name} cannot be empty.")
    return value

def handle_errors(lat, date, utc_offset, local_time, tilt, azimuth, albedo, longitude):
    # Validate all inputs
    try:
        lat = float(lat)
        if lat < -90 or lat > 90:
            raise ValueError("Latitude must be between -90 and 90.")
    except (ValueError, TypeError):
        raise ValueError("Latitude must be a number between -90 and 90.")
    
    # Validate date format
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValueError("Date must be in YYYY-MM-DD format.")
    
    try:
        utc_offset = float(utc_offset)
        if utc_offset < -12 or utc_offset > 14:
            raise ValueError("UTC offset must be between -12 and 14.")
    except (ValueError, TypeError):
        raise ValueError("UTC offset must be a number between -12 and 14.")
    
    # Validate local time format
    try:
        datetime.datetime.strptime(local_time, "%H:%M")
    except (ValueError, TypeError):
        raise ValueError("Local time must be in HH:MM (24-hour) format.")
    
    try:
        tilt = float(tilt)
        if tilt < 0 or tilt > 90:
            raise ValueError("Panel tilt must be between 0 and 90 degrees.")
    except (ValueError, TypeError):
        raise ValueError("Panel tilt must be a number between 0 and 90.")
    
    try:
        azimuth = float(azimuth)
        if azimuth < 0 or azimuth > 360:
            raise ValueError("Panel azimuth must be between 0 and 360 degrees.")
    except (ValueError, TypeError):
        raise ValueError("Panel azimuth must be a number between 0 and 360.")
    
    try:
        albedo = float(albedo)
        if albedo < 0 or albedo > 1:
            raise ValueError("Albedo must be between 0 and 1.")
    except (ValueError, TypeError):
        raise ValueError("Albedo must be a number between 0 and 1.")
    
    if longitude is not None and longitude != "":
        try:
            longitude = float(longitude)
            if longitude < -180 or longitude > 180:
                raise ValueError("Longitude must be between -180 and 180.")
        except (ValueError, TypeError):
            raise ValueError("Longitude must be a number between -180 and 180.")
    
    return lat, utc_offset, tilt, azimuth, albedo, longitude

def compute_and_plot(lat, date, utc_offset, local_time, tilt, azimuth, albedo, longitude):
    try:
        lat, utc_offset, tilt, azimuth, albedo, longitude = handle_errors(lat, date, utc_offset, local_time, tilt, azimuth, albedo, longitude)
    except ValueError as e:
        return {out_zenith: "", out_elevation: "", out_azimuth: "", out_dni: "", out_dhi: "", out_ghi: "", out_poa: "", out_plot: None, out_error: str(e)}
    
    # Compute results
    result = compute_poa(lat, date, utc_offset, local_time, tilt, azimuth, albedo, longitude)
    if result is None:
        return {out_zenith: "", out_elevation: "", out_azimuth: "", out_dni: "", out_dhi: "", out_ghi: "", out_poa: "", out_plot: None, out_error: "Computation failed (sun below horizon or invalid inputs)."}
    
    # Generate plot
    fig = plot_sky_dome(result["solar_azimuth"], result["solar_elevation"])
    
    return {
        out_zenith: f"{result['solar_zenith']:.2f}°",
        out_elevation: f"{result['solar_elevation']:.2f}°",
        out_azimuth: f"{result['solar_azimuth']:.2f}°",
        out_dni: f"{result['dni']:.2f} W/m²",
        out_dhi: f"{result['dhi']:.2f} W/m²",
        out_ghi: f"{result['ghi']:.2f} W/m²",
        out_poa: f"{result['poa']:.2f} W/m²",
        out_plot: fig,
        out_error: ""
    }

with gr.Blocks(title="Tilted Solar Irradiance Calculator", css=".error {color: red; font-weight: bold;}") as demo:
    gr.Markdown("# Tilted Solar Irradiance Calculator")
    with gr.Row():
        with gr.Column(scale=1):
            lat_in = gr.Number(label="Latitude (decimal degrees, -90 to 90)", value=40.0)
            date_in = gr.Textbox(label="Date (YYYY-MM-DD)", value="2023-06-21")
            utc_offset_in = gr.Number(label="UTC offset (hours, -12 to 14)", value=0)
            local_time_in = gr.Textbox(label="Local time (HH:MM, 24-hour)", value="12:00")
            tilt_in = gr.Number(label="Panel tilt from horizontal (0-90°)", value=30)
            azimuth_in = gr.Number(label="Panel azimuth (0-360°, 0=N, 90=E, 180=S, 270=W)", value=180)
            albedo_in = gr.Number(label="Ground albedo (0-1)", value=0.25)
            longitude_in = gr.Textbox(label="Longitude (optional, decimal degrees)", value="")
            compute_btn = gr.Button("Compute")
        with gr.Column(scale=1):
            out_zenith = gr.Textbox(label="Solar Zenith Angle", interactive=False)
            out_elevation = gr.Textbox(label="Solar Elevation", interactive=False)
            out_azimuth = gr.Textbox(label="Solar Azimuth", interactive=False)
            out_dni = gr.Textbox(label="Direct Normal Irradiance (DNI)", interactive=False)
            out_dhi = gr.Textbox(label="Diffuse Horizontal Irradiance (DHI)", interactive=False)
            out_ghi = gr.Textbox(label="Global Horizontal Irradiance (GHI)", interactive=False)
            out_poa = gr.Textbox(label="Plane-of-Array Irradiance (POA)", interactive=False)
            out_plot = gr.Plot(label="Sky Dome Plot")
            out_error = gr.HTML(label="", visible=False)
    
    compute_btn.click(
        fn=compute_and_plot,
        inputs=[lat_in, date_in, utc_offset_in, local_time_in, tilt_in, azimuth_in, albedo_in, longitude_in],
        outputs=[out_zenith, out_elevation, out_azimuth, out_dni, out_dhi, out_ghi, out_poa, out_plot, out_error]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
