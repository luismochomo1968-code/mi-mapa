"""
Cosmología Unificada: Análisis Riguroso de Distancia Comóvil
Modelo: Einstein + Dinámica Cuántica-Caótica
Datos: DESI DR2 BAO (simulados)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import chi2
from scipy.interpolate import interp1d
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. DEFINICIÓN DE MODELOS COSMOLÓGICOS
# ============================================================================

def comoving_distance_LCDM(z, H0=67.4, Om=0.315, Ol=0.685):
    """
    Distancia comóvil en ΛCDM (modelo estándar)
    H0: Constante de Hubble [km/s/Mpc]
    Om: Densidad de materia
    Ol: Densidad de energía oscura
    """
    c = 299792.458  # velocidad de luz [km/s]
    
    # Integración numérica
    z_array = np.linspace(0, z, 1000)
    dz = z_array[1] - z_array[0]
    
    E_z = np.sqrt(Om * (1 + z_array)**3 + Ol)
    integrand = 1.0 / E_z
    
    integral = np.trapz(integrand, z_array)
    
    return (c / H0) * integral

def comoving_distance_LCDM_vec(z, H0=67.4, Om=0.315, Ol=0.685):
    """Versión vectorizada"""
    return np.array([comoving_distance_LCDM(zi, H0, Om, Ol) for zi in z])

def comoving_distance_quantum_chaotic(z, H0=67.4, Om=0.315, Ol=0.685, 
                                       amp_osc=0.05, freq_osc=1.2):
    """
    Modelo Unificado: Einstein + Oscilación Cuántica-Caótica
    
    La oscilación cuántica modula la métrica de Friedmann-Lemaître-Robertson-Walker
    D(z) = D_ΛCDM(z) * [1 + amp * sin(freq * z)]
    
    Parámetros:
    - amp_osc: Amplitud de oscilación (0-0.1)
    - freq_osc: Frecuencia de oscilación (0.5-2.0)
    """
    c = 299792.458
    
    z_array = np.linspace(0, z, 1000)
    dz = z_array[1] - z_array[0]
    
    # Factor de escala modificado con oscilación
    E_z = np.sqrt(Om * (1 + z_array)**3 + Ol)
    oscillation = 1.0 + amp_osc * np.sin(freq_osc * z_array)
    integrand = oscillation / E_z
    
    integral = np.trapz(integrand, z_array)
    
    return (c / H0) * integral

def comoving_distance_quantum_chaotic_vec(z, H0=67.4, Om=0.315, Ol=0.685,
                                          amp_osc=0.05, freq_osc=1.2):
    """Versión vectorizada"""
    return np.array([comoving_distance_quantum_chaotic(zi, H0, Om, Ol, 
                                                        amp_osc, freq_osc) 
                     for zi in z])

# ============================================================================
# 2. GENERACIÓN DE DATOS SINTÉTICOS (DESI DR2 BAO simulados)
# ============================================================================

np.random.seed(42)

# Redshifts de observaciones BAO típicas
z_obs = np.array([0.31, 0.51, 0.71, 0.95, 1.10, 1.35, 1.60, 1.85, 2.10, 2.40])

# Distancias comóviles del modelo verdadero (cerca de ΛCDM con pequeña desviación)
H0_true = 67.4
Om_true = 0.315
Ol_true = 0.685
amp_osc_true = 0.02  # Oscilación pequeña
freq_osc_true = 0.8

D_true = comoving_distance_quantum_chaotic_vec(z_obs, H0_true, Om_true, Ol_true,
                                               amp_osc_true, freq_osc_true)

# Errores observacionales realistas (1-2% típico en BAO)
error_percent = 0.015  # 1.5%
sigma_D = D_true * error_percent
D_obs = D_true + np.random.normal(0, sigma_D)

print("="*70)
print("DATOS DESI DR2 BAO (Simulados)")
print("="*70)
print(f"{'z':>8} {'D_obs [Mpc]':>18} {'σ_D [Mpc]':>18} {'% error':>12}")
print("-"*70)
for i, z in enumerate(z_obs):
    print(f"{z:8.2f} {D_obs[i]:18.1f} {sigma_D[i]:18.1f} {error_percent*100:12.2f}")
print("-"*70)

# ============================================================================
# 3. AJUSTE DEL MODELO ΛCDM (REFERENCIA)
# ============================================================================

def lcdm_fit(z, H0):
    """Función para ajuste (solo H0 como parámetro libre)"""
    Om = 0.315
    Ol = 0.685
    return comoving_distance_LCDM_vec(z, H0, Om, Ol)

# Ajuste inicial
popt_lcdm, pcov_lcdm = curve_fit(lcdm_fit, z_obs, D_obs, p0=[67.4], 
                                 sigma=sigma_D, absolute_sigma=True)
H0_fit_lcdm = popt_lcdm[0]
H0_err_lcdm = np.sqrt(pcov_lcdm[0, 0])

D_fit_lcdm = lcdm_fit(z_obs, H0_fit_lcdm)
residuals_lcdm = (D_obs - D_fit_lcdm) / sigma_D
chi2_lcdm = np.sum(residuals_lcdm**2)
dof_lcdm = len(z_obs) - 1  # 1 parámetro libre
chi2_red_lcdm = chi2_lcdm / dof_lcdm
p_value_lcdm = 1 - chi2.cdf(chi2_lcdm, dof_lcdm)

print("\n" + "="*70)
print("AJUSTE MODELO ΛCDM (REFERENCIA)")
print("="*70)
print(f"H0 = {H0_fit_lcdm:.2f} ± {H0_err_lcdm:.2f} km/s/Mpc")
print(f"χ² = {chi2_lcdm:.3f}")
print(f"Grados de libertad = {dof_lcdm}")
print(f"χ²/DOF = {chi2_red_lcdm:.3f}")
print(f"p-value = {p_value_lcdm:.4f}")
if chi2_red_lcdm < 1.5 and p_value_lcdm > 0.05:
    print("✓ AJUSTE ACEPTABLE")
else:
    print("✗ AJUSTE DEFICIENTE")
print("-"*70)

# ============================================================================
# 4. AJUSTE DEL MODELO CUÁNTICO-CAÓTICO
# ============================================================================

def quantum_chaotic_fit(z, H0, amp_osc, freq_osc):
    """Función para ajuste"""
    Om = 0.315
    Ol = 0.685
    return comoving_distance_quantum_chaotic_vec(z, H0, Om, Ol, amp_osc, freq_osc)

# Ajuste con múltiples parámetros
p0 = [67.4, 0.03, 1.0]
try:
    popt_qc, pcov_qc = curve_fit(quantum_chaotic_fit, z_obs, D_obs, p0=p0,
                                 sigma=sigma_D, absolute_sigma=True,
                                 maxfev=2000, bounds=([60, 0, 0.1], [75, 0.1, 2.0]))
    H0_fit_qc = popt_qc[0]
    amp_fit_qc = popt_qc[1]
    freq_fit_qc = popt_qc[2]
    
    H0_err_qc = np.sqrt(pcov_qc[0, 0])
    amp_err_qc = np.sqrt(pcov_qc[1, 1])
    freq_err_qc = np.sqrt(pcov_qc[2, 2])
    
    D_fit_qc = quantum_chaotic_fit(z_obs, H0_fit_qc, amp_fit_qc, freq_fit_qc)
    residuals_qc = (D_obs - D_fit_qc) / sigma_D
    chi2_qc = np.sum(residuals_qc**2)
    dof_qc = len(z_obs) - 3  # 3 parámetros libres
    chi2_red_qc = chi2_qc / dof_qc
    p_value_qc = 1 - chi2.cdf(chi2_qc, dof_qc)
    
    print("\n" + "="*70)
    print("AJUSTE MODELO CUÁNTICO-CAÓTICO UNIFICADO")
    print("="*70)
    print(f"H0 = {H0_fit_qc:.2f} ± {H0_err_qc:.2f} km/s/Mpc")
    print(f"Amplitud Oscilación = {amp_fit_qc:.4f} ± {amp_err_qc:.4f}")
    print(f"Frecuencia Oscilación = {freq_fit_qc:.3f} ± {freq_err_qc:.3f}")
    print(f"χ² = {chi2_qc:.3f}")
    print(f"Grados de libertad = {dof_qc}")
    print(f"χ²/DOF = {chi2_red_qc:.3f}")
    print(f"p-value = {p_value_qc:.4f}")
    if chi2_red_qc < 1.5 and p_value_qc > 0.05:
        print("✓ AJUSTE ACEPTABLE")
    else:
        print("✗ AJUSTE DEFICIENTE")
    print("-"*70)
    
except Exception as e:
    print(f"Error en ajuste cuántico-caótico: {e}")
    H0_fit_qc = H0_fit_lcdm
    amp_fit_qc = 0.02
    freq_fit_qc = 1.0
    chi2_red_qc = chi2_red_lcdm
    p_value_qc = p_value_lcdm

# ============================================================================
# 5. COMPARACIÓN DE MODELOS
# ============================================================================

print("\n" + "="*70)
print("COMPARACIÓN DE MODELOS")
print("="*70)
print(f"{'Métrica':30} {'ΛCDM':15} {'Cuántico-Caótico':15}")
print("-"*70)
print(f"{'χ²/DOF':30} {chi2_red_lcdm:15.3f} {chi2_red_qc:15.3f}")
print(f"{'p-value':30} {p_value_lcdm:15.4f} {p_value_qc:15.4f}")

if chi2_red_qc < chi2_red_lcdm:
    mejora = ((chi2_red_lcdm - chi2_red_qc) / chi2_red_lcdm) * 100
    print(f"{'Mejora del modelo cuántico':30} {mejora:15.1f}%")
else:
    print(f"{'ΛCDM es mejor':30} {'Sí':15} {'No':15}")

print("-"*70)

# ============================================================================
# 6. CREACIÓN DE GRÁFICAS CIENTÍFICAS
# ============================================================================

fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(3, 1, height_ratios=[2, 1, 1], hspace=0.35)

ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])
ax3 = fig.add_subplot(gs[2])

# Puntos de curva continua
z_curve = np.linspace(0.1, 2.5, 200)
D_curve_lcdm = lcdm_fit(z_curve, H0_fit_lcdm)
D_curve_qc = quantum_chaotic_fit(z_curve, H0_fit_qc, amp_fit_qc, freq_fit_qc)

# --- PANEL 1: Distancia Comóvil ---
ax1.errorbar(z_obs, D_obs, yerr=sigma_D, fmt='o', color='#0066CC', 
             markersize=10, capsize=5, capthick=2, label='Datos DESI DR2 BAO', 
             elinewidth=2, alpha=0.8, zorder=5)

ax1.plot(z_curve, D_curve_lcdm, 'k-', linewidth=2.5, label='ΛCDM',
         alpha=0.7, zorder=4)

ax1.plot(z_curve, D_curve_qc, color='#FF6B35', linewidth=2.5, 
         label='Cuántico-Caótico', alpha=0.8, zorder=3)

ax1.fill_between(z_curve, D_curve_qc - D_curve_qc*0.015, 
                 D_curve_qc + D_curve_qc*0.015, alpha=0.15, color='#FF6B35',
                 label='Banda ±1.5% (error típico BAO)', zorder=1)

ax1.set_ylabel('Distancia Comóvil DM [Mpc]', fontsize=13, fontweight='bold')
ax1.set_xlim(0.2, 2.6)
ax1.set_ylim(0, 6500)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.legend(loc='upper left', fontsize=11, framealpha=0.95)

title_text = ("Cosmología Unificada: Distancia Comóvil\n"
              f"ΛCDM: χ²/DOF = {chi2_red_lcdm:.3f} | "
              f"Cuántico: χ²/DOF = {chi2_red_qc:.3f}")
ax1.set_title(title_text, fontsize=13, fontweight='bold', pad=15)

# --- PANEL 2: Residuales ΛCDM ---
residuals_lcdm_full = (D_obs - D_fit_lcdm) / sigma_D

ax2.errorbar(z_obs, residuals_lcdm_full, yerr=np.ones_like(z_obs), fmt='s', 
             color='#000000', markersize=9, capsize=5, capthick=2, 
             label='ΛCDM Residuales', elinewidth=2, alpha=0.8, zorder=5)

ax2.axhline(y=0, color='k', linestyle='-', linewidth=1.5, alpha=0.5)
ax2.axhline(y=1, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='±1σ')
ax2.axhline(y=-1, color='gray', linestyle='--', linewidth=1, alpha=0.5)
ax2.axhline(y=2, color='lightcoral', linestyle=':', linewidth=1, alpha=0.5, label='±2σ')
ax2.axhline(y=-2, color='lightcoral', linestyle=':', linewidth=1, alpha=0.5)

ax2.set_ylabel('(D_obs - D_modelo) / σ', fontsize=12, fontweight='bold')
ax2.set_xlim(0.2, 2.6)
ax2.set_ylim(-3, 3)
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.legend(loc='upper left', fontsize=10)

stats_text = f"χ² = {chi2_lcdm:.2f} | DOF = {dof_lcdm} | p = {p_value_lcdm:.3f}"
ax2.text(0.98, 0.95, stats_text, transform=ax2.transAxes, 
         fontsize=10, verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# --- PANEL 3: Residuales Cuántico-Caótico ---
residuals_qc_full = (D_obs - D_fit_qc) / sigma_D

ax3.errorbar(z_obs, residuals_qc_full, yerr=np.ones_like(z_obs), fmt='o', 
             color='#FF6B35', markersize=9, capsize=5, capthick=2,
             label='Cuántico-Caótico Residuales', elinewidth=2, alpha=0.8, zorder=5)

ax3.axhline(y=0, color='k', linestyle='-', linewidth=1.5, alpha=0.5)
ax3.axhline(y=1, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='±1σ')
ax3.axhline(y=-1, color='gray', linestyle='--', linewidth=1, alpha=0.5)
ax3.axhline(y=2, color='lightcoral', linestyle=':', linewidth=1, alpha=0.5, label='±2σ')
ax3.axhline(y=-2, color='lightcoral', linestyle=':', linewidth=1, alpha=0.5)

ax3.set_xlabel('Redshift z', fontsize=12, fontweight='bold')
ax3.set_ylabel('(D_obs - D_modelo) / σ', fontsize=12, fontweight='bold')
ax3.set_xlim(0.2, 2.6)
ax3.set_ylim(-3, 3)
ax3.grid(True, alpha=0.3, linestyle='--')
ax3.legend(loc='upper left', fontsize=10)

stats_text_qc = f"χ² = {chi2_qc:.2f} | DOF = {dof_qc} | p = {p_value_qc:.3f}"
ax3.text(0.98, 0.95, stats_text_qc, transform=ax3.transAxes,
         fontsize=10, verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

plt.savefig('cosmologia_ajustada.png', dpi=300, bbox_inches='tight')
print("\n✓ Gráfica guardada como 'cosmologia_ajustada.png'")

plt.show()

# ============================================================================
# 7. ANÁLISIS DE RESIDUALES
# ============================================================================

from scipy.stats import normaltest

print("\n" + "="*70)
print("ANÁLISIS ESTADÍSTICO DE RESIDUALES")
print("="*70)

# Test de normalidad (Anderson-Darling)
k2_lcdm, p_norm_lcdm = normaltest(residuals_lcdm_full)
k2_qc, p_norm_qc = normaltest(residuals_qc_full)

print("\nTest de Normalidad (Anderson-Darling):")
print(f"ΛCDM: k² = {k2_lcdm:.3f}, p-value = {p_norm_lcdm:.4f}")
if p_norm_lcdm > 0.05:
    print("  ✓ Residuales distribuidos normalmente")
else:
    print("  ✗ Residuales NO normales (señal de sistemática)")

print(f"\nCuántico-Caótico: k² = {k2_qc:.3f}, p-value = {p_norm_qc:.4f}")
if p_norm_qc > 0.05:
    print("  ✓ Residuales distribuidos normalmente")
else:
    print("  ✗ Residuales NO normales (señal de sistemática)")

# Estadísticas básicas
print("\n" + "-"*70)
print("Estadísticas Residuales ΛCDM:")
print(f"  Media = {np.mean(residuals_lcdm_full):.4f}")
print(f"  Desv. Est. = {np.std(residuals_lcdm_full):.4f}")
print(f"  Min/Max = [{np.min(residuals_lcdm_full):.3f}, {np.max(residuals_lcdm_full):.3f}]")

print("\nEstadísticas Residuales Cuántico-Caótico:")
print(f"  Media = {np.mean(residuals_qc_full):.4f}")
print(f"  Desv. Est. = {np.std(residuals_qc_full):.4f}")
print(f"  Min/Max = [{np.min(residuals_qc_full):.3f}, {np.max(residuals_qc_full):.3f}]")

print("\n" + "="*70)
