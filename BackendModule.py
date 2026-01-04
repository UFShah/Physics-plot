
import dis
from matplotlib import rc
from matplotlib.transforms import Bbox
import numpy as np
import matplotlib.pyplot as plt
import scienceplots
from numpy._typing._array_like import NDArray
from matplotlib.figure import Figure
from tkinter import filedialog, font
from typing import Any
from scipy.odr._odrpack import Output
from scipy.optimize import curve_fit
from scipy.odr import ODR, Model, RealData
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import sys
import os

def resource(relative_path):
    """Get the absolute path to a resource, works for dev and PyInstaller one-file bundles."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

plt.style.use([resource('science.mplstyle'), resource('notebook.mplstyle'), resource('grid.mplstyle')])
from CTkMessagebox import CTkMessagebox





class HistogramMaker ():
    def __init__(self, values, title,  sig_show_bool, no_of_stds, sig_draw_bool, normalized,  bins=10, xlabel="Bins", ylabel="Probability Density" ) -> None:
        self.values: NDArray = values
        self.title: str = title
        self.sig_show_bool:bool = sig_show_bool
        self.no_of_stds:float = no_of_stds
        self.sig_draw_bool:bool = sig_draw_bool
        self.normalized:bool = normalized
        self.bins: int = bins
        self.xlabel: str = xlabel
        self.ylabel: str = ylabel
        
        self.precision = 4
        
        self.std_val:float  =float(np.std(self.values))
        self.sigma_str = fr"{self.no_of_stds}$\sigma={self.no_of_stds*self.std_val:.{self.precision}g}$"
        self.vals_mean: float = float(np.mean(self.values))
        
    def histogramcreater (self):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        ax = self.fig.add_subplot(111)
        counts, edges, patches= ax.hist(self.values, bins=self.bins, density=self.normalized)
        ax.set_xticks(edges)
        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)

        if self.sig_show_bool == True:
            ax.text(0.05, 0.9, self.sigma_str, transform=ax.transAxes, fontsize=20, bbox=dict(facecolor= "white", edgecolor="black") )
        if self.sig_draw_bool == True:    
            ax.axvline(self.vals_mean + (self.no_of_stds*self.std_val), color='red', linestyle='--', linewidth=1.5, label=f'+{self.no_of_stds} Std Dev: {self.vals_mean + (self.no_of_stds*self.std_val):.2f}')
            ax.axvline(self.vals_mean - (self.no_of_stds*self.std_val), color='red', linestyle='--', linewidth=1.5, label=f'-{self.no_of_stds} Std Dev: {self.vals_mean - (self.no_of_stds*self.std_val):.2f}')
            ax.legend()
        return self.fig
        
    def histogram_saver(self) -> None:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            self.fig.savefig(file_path)


class ScatterMaker ():
    def __init__(self, x_values, y_values, p0, sigmax, sigmay, model_picker_value, xname, yname, titlename, disp_bools) -> None:
        
        self.x_values:NDArray = x_values
        self.y_values:NDArray = y_values
        self.p0: tuple = p0
        self.sigmax:NDArray | None = sigmax
        self.sigmay:NDArray | None = sigmay
        
        self.model_picker_value:int = model_picker_value
        self.xname: str = xname
        self.yname: str = yname
        self.titlename: str = titlename
        self.fit_line_disp: bool = disp_bools[0]
        self.disp_eq: bool = disp_bools[1]
        self.dis_r2: bool = disp_bools[2]
        self.disp_sigmval: bool = disp_bools[3]
        self.param_disp: bool = disp_bools[4]
        self.chi_chkr: bool = disp_bools[5]
        self.rd_chi_chkr: bool = disp_bools[6]
        self.ind_var_name: str = "y"
        self.dep_var_name: str = "x"
        self.fig = Figure(figsize=(5, 4), dpi=100)
        
        
    def sccater_creater(self):
        
        ax = self.fig.add_subplot(111)

        ax.set_title(self.titlename)
        ax.set_xlabel(self.xname)
        ax.set_ylabel(self.yname)
        self.max_x = np.max(self.x_values)+1
        self.min_x = np.min(self.x_values)-1
        self.xplot = np.linspace(self.min_x, self.max_x, 24)
        self.sigmax:NDArray | None = length_checker(self.sigmax, len(self.x_values))
        self.sigmay:NDArray | None = length_checker(self.sigmay, len(self.y_values))
        
        if self.sigmax is not None or self.sigmay is not None:
            ax.errorbar(self.x_values, self.y_values, xerr=self.sigmax, yerr=self.sigmay, fmt='ko', capsize=4)
        
        
        if self.p0 is not None:
            self.reg_params , self.reg_covmat = curve_fit(self.model_pkr_ols(), self.x_values, self.y_values, self.p0, sigma=self.sigmay)
        
        
        if self.sigmax is None:
            #self.sigx_bool: bool = False
            self.params  = self.reg_params
            self.covmat = np.sqrt(np.diag(self.reg_covmat))
            self.sigma_y_eff:float = np.sqrt(sum((rifun(self.model_pkr_ols(), self.x_values, self.y_values, self.params))**2)/(len(self.y_values) - 2))
            self.fitequation = self.fit_model_maker(self.params)
            self.r2 = 1- sum((self.y_values - self.fitequation)**2)/sum((self.y_values - np.mean(self.y_values))**2)   
        elif self.sigmax is not None:
            #self.sigx_bool: bool = True
            data: RealData = RealData(self.x_values, self.y_values, sx=self.sigmax, sy=self.sigmay)
            model: Model = Model(self.model_pkr_odr())
            odr: ODR= ODR(data, model, beta0=self.reg_params)
            output: Output = odr.run()
            self.params = output.beta
            self.fitequation = self.fit_model_maker(self.params)
            self.r2 = 1- sum((self.y_values - self.fitequation)**2)/sum((self.y_values - self.y_values.mean())**2)

            self.covmat = output.sd_beta
            self.sigma_y_eff = np.sqrt(np.mean(rifun(self.model_pkr_ols(), self.x_values, self.y_values, self.params)**2))


        ufit: str = fr"$σ_{{{self.ind_var_name}}} = {round(self.sigma_y_eff,3)}$"
        if self.disp_eq == True and self.disp_sigmval == False:
            
            ax.text(0.01, 0.85, self.scat_text(), transform=ax.transAxes,
                verticalalignment="top",fontsize=15, bbox=dict(facecolor= "white", edgecolor="black") )
        if self.disp_sigmval == True and self.disp_eq == False:
            
            ax.text(0.01, 0.90, ufit, transform=ax.transAxes, fontsize=20, 
                    bbox=dict(facecolor= "white", edgecolor="black") )
        elif self.disp_sigmval == True and self.disp_eq == True:
            
            ax.text(0.01, 0.75, self.scat_text() + "\n"+ufit, transform=ax.transAxes, fontsize=20, 
                    bbox=dict(facecolor= "white", edgecolor="black") )
            
        if self.fit_line_disp == True:
            ax.plot(self.x_values, self.fitequation, 'k-')
        if self.dis_r2 == True:
            r2_str: str = fr"$r^2 = {round(self.r2,3)}$"
            ax.text(0.7, 1.03, r2_str, transform=ax.transAxes, fontsize=20, 
                    bbox=dict(facecolor= "white", edgecolor="black") )
            
        if self.chi_chkr == True or self.rd_chi_chkr == True:
            chi2, rchi2 = self.chi2_and_rchi2_disp()
            if self.chi_chkr == True and self.rd_chi_chkr == True:
                chi2_str, rchi2_str = self.flt_to_str()
                ax.text(0.29, 0.85, chi2_str + "\n" + rchi2_str, transform=ax.transAxes, fontsize=20, 
                        bbox=dict(facecolor= "white", edgecolor="black") )
            elif self.chi_chkr ==True:
                chi2_str: str = fr"$\chi^2 = {round(chi2,3)}$"
                ax.text(0.29, 0.90, chi2_str, transform=ax.transAxes, fontsize=20, 
                        bbox=dict(facecolor= "white", edgecolor="black") )
            elif self.rd_chi_chkr == True:
                rchi2_str: str = fr"$\chi^2_v = {round(rchi2,3)}$"
                ax.text(0.29, 0.90, rchi2_str, transform=ax.transAxes, fontsize=20, 
                        bbox=dict(facecolor= "white", edgecolor="black") )
            

                



        ax.scatter(self.x_values, self.y_values, s=25, c="black" )
        
        return self.fig
    
    def scat_saver(self) -> None:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            self.fig.savefig(file_path)

    
        
    def model_pkr_ols (self):
        if self.model_picker_value == 1:
            #self.p0 = 1,0
            return f_linear
        elif self.model_picker_value == 2:
            #self.p0 = 0,1,1
            return quadratic_func
        elif self.model_picker_value == 3:
            #self.p0 = 1,0
            return inverse_square
        elif self.model_picker_value == 4:
            #self.p0 = 1,1
            return f_exponential
        elif self.model_picker_value == 5:
            #self.p0 = 1, 1, 0
            return log_func

    def model_pkr_odr (self):
        if self.model_picker_value == 1:   return f_linear_odr
        elif self.model_picker_value == 2: return quadratic_func_odr
        elif self.model_picker_value == 3: return inverse_square_odr
        elif self.model_picker_value == 4: return f_exponential_odr
        elif self.model_picker_value == 5: return log_func_odr
        
    def fit_model_maker (self, params) -> NDArray:
        if self.model_picker_value == 1:
            return f_linear(self.x_values, *params)
        elif self.model_picker_value == 2:
            return quadratic_func (self.x_values, *params)
        elif self.model_picker_value == 3:
            return inverse_square(self.x_values, *params)
        elif self.model_picker_value == 4:
            return f_exponential(self.x_values, *params)
        else:
            return log_func(self.x_values, *params)
    
    def scat_text(self) -> str:
        if self.model_picker_value in [1, 3, 4]:
                
            eq, sl, interc = str_mkr(self.model_picker_value, self.ind_var_name, self.dep_var_name, self.params, self.covmat)
            if self.param_disp == True:
                tot_str = eq +"\n"+ sl + "\n" + interc
            else:
                tot_str = eq
        

            return tot_str 
        else:
            eq, a_str, b_str, c_str = str_mkr_3par(self.model_picker_value, self.ind_var_name, self.dep_var_name, self.params, self.covmat)
            tot_str = eq +"\n"+ a_str + "\n" + b_str + "\n" + c_str

            return tot_str

    def chi2_and_rchi2_disp (self):
        if self.sigmay is None:
            chi2:float; rchi2:float; [chi2 , rchi2] = chi_squared(self.y_values, self.fitequation, self.sigma_y_eff, np.zeros_like(self.y_values), self.model_picker_value)
        else:
            chi2:float; rchi2:float; [chi2 , rchi2] =chi_squared(self.y_values, self.fitequation, self.sigma_y_eff, self.sigmay, self.model_picker_value)
        return [chi2, rchi2]
    
    def flt_to_str(self) -> tuple[str, str]:
        chi2, rchi2 = self.chi2_and_rchi2_disp()
        chi2_str: str = fr"$\chi^2 = {round(chi2,3)}$"
        rchi2_str: str = fr"$\chi^2_v = {round(rchi2,3)}$"
        return chi2_str, rchi2_str
    
    def ufit_str(self) -> str:
        ufit: str = fr"σ = {round(self.sigma_y_eff,3)}"
        return ufit
    def eq_flt_to_str(self) -> list[str]:
        if self.model_picker_value in [1, 3, 4]:
            eq, sl, interc = str_printer(self.model_picker_value, self.ind_var_name, self.dep_var_name, self.params, self.covmat)
            return [eq, sl, interc]
        else:
            eq, a_str, b_str, c_str = str_printer_3par(self.model_picker_value, self.ind_var_name, self.dep_var_name, self.params, self.covmat)
            tot_str = eq +"\n"+ a_str + "\n" + b_str + "\n" + c_str

            return [eq, a_str, b_str + "\n"+ c_str]

    
        
            
            
            


        
#-----------------------------   

#model functions for scipy.optimize curve_fit     
#linear function
def f_linear (x, m, b):
    """
    
    x is the x-values & they should be in an numpy array format
    m & b are constant they can be single variable or an arrary

    """
    return m*x + b

#quadratic function
def quadratic_func(
    x:np.ndarray,
    a:Any,
    b:Any,
    c:Any):
    return a * np.square(x) + b * x + c

#inverse square
def inverse_square (
    r:np.ndarray,
    a, b):
    return (a/(np.square(r))) + b

#exponential function
def f_exponential (x, a, b):
    return b*np.exp(a*x)


def log_func(x, a, b, c):
    """
    Natural log model for curve fitting.
    a: scaling factor
    b: horizontal shift (prevents log(0) if data starts at 0)
    c: vertical shift
    """
    return a * np.log(x + b) + c
    
#-----------------------------

#Model functions for ODR

#linear function
def f_linear_odr (B, x):
    """
    
    x is the x-values & they should be in an numpy array format
    B is an array of parameters [m, b]

    """
    return B[0]*x + B[1]

#quadratic function
def quadratic_func_odr(
    B:NDArray,
    x:np.ndarray):
    return B[0] * np.square(x) + B[1] * x + B[2]

#inverse square
def inverse_square_odr (B:NDArray, r:np.ndarray)-> Any:
    return (B[0]/(np.square(r))) + B[1]

#exponential function
def f_exponential_odr (B:NDArray, x:np.ndarray)-> Any:
    return B[1]*np.exp(B[0]*x)

#logarithmic function
def log_func_odr(B:NDArray, x:np.ndarray)-> Any:
    """
    
    Natural log model for ODR.
    B: array of parameters [a, b, c]
    a: scaling factor
    b: horizontal shift (prevents log(0) if data starts at 0)
    c: vertical shift
    
    """
    return B[0] * np.log(x + B[1]) + B[2]

#------------------------------
# Utility functions
def length_checker (array, desired_length) -> NDArray | None:
    try:
        if len(array) == 1:
            return np.full(desired_length, array[0])
        elif len(array) == desired_length:
            return array
        elif array is None:
            return None
        else:
            CTkMessagebox(title="Error", message="Length of uncertainty array does not match data length.")
    except:
        pass

def rifun(function,x_values, y_values, params) -> NDArray:
    rii: NDArray = y_values - function(x_values, *params)
    return rii 

def str_mkr(mpv, ivname, dvname, params, covmat ) -> tuple[str, str, str]:
    if mpv == 1:
        eq: str = fr"${{{ivname}}} = {round(params[0], 2)}{{{dvname}}} + {round(params[1], 4)}$"
        sl: str = fr"$m = {round(params[0], 2)} \pm {round(covmat[0], 2)}$"
        interc: str = fr"$b = {round(params[1], 4)} \pm {round(covmat[1], 4)}$"
        return eq, sl, interc
    elif mpv == 3:
        eq: str = fr"${{{ivname}}} = \frac{{{round(params[0], 2)}}} {{{{{dvname}}}^2}} + {round(params[1], 4)}$"
        sl: str = fr"$a = {round(params[0], 2)} \pm {round(covmat[0], 2)}$"
        interc: str = fr"$b = {round(params[1], 4)} \pm {round(covmat[1], 4)}$"
        return eq, sl, interc
    elif mpv == 4:
        eq: str = fr"${{{ivname}}} = {round(params[1], 2)}e^{{{round(params[0], 2)}{{{dvname}}}}}$"
        a_str: str = fr"$a = {round(params[0], 2)} \pm {round(covmat[0], 2)}$"
        b_str: str = fr"$b = {round(params[1], 4)} \pm {round(covmat[1], 4)}$"
        return eq, a_str, b_str
    else:
        return "", "", ""

def str_mkr_3par(mpv, ivname, dvname, params, covmat) -> tuple[str, str, str, str]:
    if mpv == 2:
        eq: str = fr"${{{ivname}}} = {round(params[0], 2)}{{{dvname}}}^2 + {round(params[1], 2)}{{{dvname}}} + {round(params[2], 4)}$"
        a_str: str = fr"$a = {round(params[0], 2)} \pm {round(covmat[0], 2)}$"
        b_str: str = fr"$b = {round(params[1], 2)} \pm {round(covmat[1], 2)}$"
        c_str: str = fr"$c = {round(params[2], 4)} \pm {round(covmat[2], 4)}$"
        return eq, a_str, b_str, c_str
    elif mpv == 5:
        eq: str = fr"${{{ivname}}} = {round(params[0], 2)} \ln({{{dvname}}} + {round(params[1], 2)}) + {round(params[2], 4)}$"
        a_str: str = fr"$a = {round(params[0], 2)} \pm {round(covmat[0], 2)}$"
        b_str: str = fr"$b = {round(params[1], 2)} \pm {round(covmat[1], 2)}$"
        c_str: str = fr"$c = {round(params[2], 4)} \pm {round(covmat[2], 4)}$"
        return eq, a_str, b_str, c_str
    else:
        return "", "", "", ""

def chi_squared(y_obs, y_exp, ufit, sigmay, mdl_len) :# -> list[Any]:
    chi2: float = sum((y_obs - y_exp)**2/(ufit**2 + sigmay**2))
    if mdl_len in [1, 3, 4]:
        rchi2: float = chi2/(len(y_obs) -  2)
    else:
        rchi2: float = chi2/(len(y_obs) -  3)
    return [chi2, rchi2]

def str_printer(mpv, ivname, dvname, params, covmat ) :
    if mpv == 1:
        eq: str = fr"{ivname} = {round(params[0], 2)}{dvname} + {round(params[1], 4)}"
        sl: str = fr"m = {round(params[0], 2)} ± {round(covmat[0], 2)}"
        interc: str = fr"b = {round(params[1], 4)} ± {round(covmat[1], 4)}"
        return [eq, sl, interc]
    elif mpv == 3:
        eq: str = fr"{ivname} = {round(params[0], 2)}/{dvname}² + {round(params[1], 4)}"
        sl: str = fr"a = {round(params[0], 2)} ± {round(covmat[0], 2)}"
        interc: str = fr"b = {round(params[1], 4)} ± {round(covmat[1], 4)}"
        return [eq, sl, interc]
    elif mpv == 4:
        eq: str = fr"{ivname} = {round(params[1], 2)}e{flt_to_supscrpt(round(params[0], 2)+dvname)}"
        a_str: str = fr"a = {round(params[0], 2)} ± {round(covmat[0], 2)}"
        b_str: str = fr"b = {round(params[1], 4)} ± {round(covmat[1], 4)}"
        return [eq, a_str, b_str]
    else:
        return ["", "", ""]

def str_printer_3par(mpv, ivname, dvname, params, covmat)   -> list[str]:
    if mpv == 2:
        eq: str = fr"{ivname} = {round(params[0], 2)}{dvname}² + {round(params[1], 2)}{dvname} + {round(params[2], 4)}"
        a_str: str = fr"a = {round(params[0], 2)} ± {round(covmat[0], 2)}"
        b_str: str = fr"b = {round(params[1], 2)} ± {round(covmat[1], 2)}"
        c_str: str = fr"c = {round(params[2], 4)} ± {round(covmat[2], 4)}"
        return [eq, a_str, b_str, c_str]
    elif mpv == 5:
        eq: str = fr"{ivname} = {round(params[0], 2)} ln({dvname} + {round(params[1], 2)}) + {round(params[2], 4)}"
        a_str: str = fr"a = {round(params[0], 2)} ± {round(covmat[0], 2)}"
        b_str: str = fr"b = {round(params[1], 2)} ± {round(covmat[1], 2)}"
        c_str: str = fr"c = {round(params[2], 4)} ± {round(covmat[2], 4)}"
        return [eq, a_str, b_str, c_str]
    else:
        return ["", "", "", ""]

# Expanded mapping for floats
sup_map = {
    # Digits
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    
    # Lowercase Letters
    "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ", "e": "ᵉ",
    "f": "ᶠ", "g": "ᵍ", "h": "ʰ", "i": "ⁱ", "j": "ʲ",
    "k": "ᵏ", "l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ",
    "p": "ᵖ", "q": "q", # No superscript 'q' in Unicode
    "r": "ʳ", "s": "ˢ", "t": "ᵗ", "u": "ᵘ", "v": "ᵛ",
    "w": "ʷ", "x": "ˣ", "y": "ʸ", "z": "ᶻ",
    
    # Uppercase Letters (Limited availability)
    "A": "ᴬ", "B": "ᴮ", "C": "ᶜ", "D": "ᴰ", "E": "ᴱ",
    "G": "ᴳ", "H": "ᴴ", "I": "ᴵ", "J": "ᴶ", "K": "ᴷ",
    "L": "ᴸ", "M": "ᴹ", "N": "ᴺ", "O": "ᴼ", "P": "ᴾ",
    "R": "ᴿ", "T": "ᵀ", "U": "ᵁ", "V": "ⱽ", "W": "ᵂ",
    
    # Symbols
    ".": "·", "-": "⁻", "+": "⁺", "=": "⁼", "(": "⁽", ")": "⁾"
}
def flt_to_supscrpt(value: float) -> str:
    str_value = str(value)
    return ''.join(sup_map.get(char, char) for char in str_value)