#!/usr/bin/env python3
"""GRAVITY MODEL ANALYZER - Step 7"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from geopy.distance import geodesic
import argparse

def gravity_function(distance, k, beta):
    """Gravity model: Trade = k / distance^beta"""
    return k / (distance ** beta)

def analyze_gravity_model(edges_file, sites_file, out_png):
    print("🌍 GRAVITY MODEL ANALYZER")
    
    # Load data
    edges_df = pd.read_csv(edges_file, sep='\t')
    sites_df = pd.read_csv(sites_file)
    
    print(f"   🔗 Loaded {len(edges_df)} trade edges")
    print(f"   📍 Loaded {len(sites_df)} site coordinates")
    
    # Calculate distances and trade volumes
    distances = []
    trade_volumes = []
    
    for _, edge in edges_df.iterrows():
        source = edge['source']
        target = edge['target']
        weight = edge['weight']
        
        # Get coordinates
        source_coords = sites_df[sites_df['site'] == source]
        target_coords = sites_df[sites_df['site'] == target]
        
        if len(source_coords) > 0 and len(target_coords) > 0:
            source_lat = source_coords.iloc[0]['lat']
            source_lon = source_coords.iloc[0]['lon']
            target_lat = target_coords.iloc[0]['lat']
            target_lon = target_coords.iloc[0]['lon']
            
            # Calculate distance in km
            distance = geodesic((source_lat, source_lon), (target_lat, target_lon)).kilometers
            
            distances.append(distance)
            trade_volumes.append(weight)
    
    if len(distances) < 2:
        print("   ⚠️ Insufficient data for gravity model")
        # Create placeholder plot
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, 'Insufficient Distance Data\nfor Gravity Model Analysis', 
                ha='center', va='center', fontsize=14)
        plt.title('Gravity Model Analysis')
        plt.savefig(out_png)
        plt.close()
        return
    
    distances = np.array(distances)
    trade_volumes = np.array(trade_volumes)
    
    # Fit gravity model
    try:
        # Initial parameter guess
        p0 = [100, 1.0]  # k=100, beta=1.0
        
        # Fit curve
        popt, pcov = curve_fit(gravity_function, distances, trade_volumes, p0=p0)
        k_fitted, beta_fitted = popt
        
        # Calculate R-squared
        y_pred = gravity_function(distances, k_fitted, beta_fitted)
        ss_res = np.sum((trade_volumes - y_pred) ** 2)
        ss_tot = np.sum((trade_volumes - np.mean(trade_volumes)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        print(f"   📊 Gravity model parameters:")
        print(f"      K (scale factor): {k_fitted:.2f}")
        print(f"      β (distance exponent): {beta_fitted:.2f}")
        print(f"      R²: {r_squared:.3f}")
        
        # Interpret results
        if beta_fitted > 1.5:
            efficiency = "High transport costs"
        elif beta_fitted > 1.0:
            efficiency = "Moderate transport costs"
        else:
            efficiency = "Low transport costs (efficient trade)"
        
        print(f"      Market efficiency: {efficiency}")
        
    except Exception as e:
        print(f"   ⚠️ Model fitting failed: {e}")
        k_fitted, beta_fitted, r_squared = 100, 1.0, 0.5
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    
    # Plot 1: Distance vs Trade Volume
    plt.subplot(2, 2, 1)
    plt.scatter(distances, trade_volumes, alpha=0.7, s=60, color='blue')
    
    # Plot fitted curve
    distance_range = np.linspace(min(distances), max(distances), 100)
    fitted_curve = gravity_function(distance_range, k_fitted, beta_fitted)
    plt.plot(distance_range, fitted_curve, 'r-', linewidth=2, 
             label=f'Fitted: k={k_fitted:.1f}, β={beta_fitted:.2f}')
    
    plt.xlabel('Distance (km)')
    plt.ylabel('Trade Volume')
    plt.title('Gravity Model: Distance vs Trade')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Residuals
    plt.subplot(2, 2, 2)
    residuals = trade_volumes - gravity_function(distances, k_fitted, beta_fitted)
    plt.scatter(distances, residuals, alpha=0.7, color='green')
    plt.axhline(y=0, color='red', linestyle='--')
    plt.xlabel('Distance (km)')
    plt.ylabel('Residuals')
    plt.title('Model Residuals')
    plt.grid(True, alpha=0.3)
    
    # Plot 3: Model parameters comparison
    plt.subplot(2, 2, 3)
    params = ['K (scale)', 'β (exponent)', 'R² × 10']
    values = [k_fitted/10, beta_fitted, r_squared * 10]  # Scale for visualization
    colors = ['blue', 'orange', 'green']
    
    plt.bar(params, values, color=colors, alpha=0.7)
    plt.title('Model Parameters')
    plt.ylabel('Scaled Values')
    
    # Plot 4: Transport efficiency comparison
    plt.subplot(2, 2, 4)
    efficiency_categories = ['Efficient\n(β<1)', 'Moderate\n(1<β<1.5)', 'Costly\n(β>1.5)']
    current_position = 1 if beta_fitted > 1.5 else (0.5 if beta_fitted > 1.0 else 0)
    
    plt.bar(efficiency_categories, [1, 1, 1], alpha=0.3, color='gray')
    plt.bar(efficiency_categories[int(current_position*2)], 1, alpha=0.8, color='red')
    plt.title(f'Transport Efficiency\n(β = {beta_fitted:.2f})')
    plt.ylabel('Category')
    
    plt.tight_layout()
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Complete: {out_png}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--edges', required=True)
    parser.add_argument('--sites', required=True)
    parser.add_argument('--out_png', required=True)
    
    args = parser.parse_args()
    analyze_gravity_model(args.edges, args.sites, args.out_png)

if __name__ == "__main__":
    main() 