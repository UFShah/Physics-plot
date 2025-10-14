from matplotlib import transforms
from pylab import *
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from numpy.typing import ArrayLike
from typing import Callable, Final, Type, Any
import numpy as np
""" This is a basic chart plotter for any linear (for now) equation with the best fit curve \n
and plotting the points. The graphingfun() gives the basic fit plot and the relevant fit equation \n
with all the errors and the coefficient of determination. \n\n
The 
"""

# Parametize model (function) that should fit data; here linear:  y = mx + b
SUB: Final[list] = str.maketrans("0123456789-", "₀₁₂₃₄₅₆₇₈₉₋")
print (SUB)

# Get the fit parameters (here, m and b) and covariance matrix from curve_fit
# make initial guess for fit parameters and assign to p0
# Weight the dependent variable by sigmay, the array of standard uncertainties

def sstotal(y: ArrayLike | None) -> ArrayLike:
    return sum((float(y) - y.mean)**2)


def scatterplthfun(
    x: ArrayLike | None,
    y: ArrayLike | None,
    linestyle="-",
    linewidth = 1, 
    xname= "X-axis",
    yname="Y-axis",
    filename_prefix="Plot",
    show_bool = "False",
    save_bool = "True"):
    
    """
    
    x and u are Arrays \n\n
    All other parameters are optional and are related to how graphs look \n\n
    and the last 3 parameters are about the filename and whether to save the graph or \n
    show it or both
    """
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, linestyle=linestyle, linewidth=linewidth)
    plt.xlabel(xname)
    plt.ylabel(yname)
    plt.title(f"{xname.translate(SUB)} vs {yname.translate(SUB)}" )
    plt.grid(True)
    if show_bool =="True" and save_bool == "True":
            plt.savefig(f"{filename_prefix}.png")
            plt.show()    
    elif show_bool == "True" and save_bool == "False":
        plt.show()
    elif show_bool == "False" and save_bool == "True":
        plt.savefig(f"{filename_prefix}.png")
        

    
    

def graphingfun(
    function: Callable[[ArrayLike, float], float],
    x: ArrayLike | None,
    y: ArrayLike,
    parameters: ArrayLike, 
    sigmaval = [0.0],  
    xname= "X-axis",
    yname="Y-axis",
    filename_prefix="Plot",
    plot_bool = "False",
    show_bool = "False",
    save_bool = "True") -> ArrayLike | Any:
    """
    
    
    For function there is one variable, first position and float can be any number of Parameters. \n\n
    x and y are Arrays \n\n
    p0 are the arbitrary constants \n\n
    sigma can be any standard deviation Array or a single value or can be left empty \n\n
    Use the xname="your x-axis name" or yname="your y-axis name" to give your preferred axis titles \n\n
    Outputs png files for best fit graphs and returns a residual values so it can be used for histograms 
    
    
    """
    if float(sigmaval[0]) != 0:
        (params, covmat) = curve_fit(function, x, y, parameters, sigma=sigmaval, absolute_sigma=True)
    else:
        params = np.polyfit(x,y,1)
        covmat = np.cov(x,y)



    # Model's prediction for the dependent variable
    # The * before params means that this is a list with an arbitrary number of
    # elements; 
    fitequation = function(x, *params)
    
    def rifun():
        for i in range (0, len(x)-1):
            rii = y - function(x[i], *params)
        return rii
            
            
    if plot_bool == "False":

        # First plot the data as black dots ('ko')
        # include dependent variable uncertainties as error bars with caps
        reggraph = plt.figure()
        plt.errorbar(x, y, yerr=sigmaval, fmt='ko', capsize=4)

        # # Overlay model, the fit result, as a straight black line ('k-')
        plt.plot(x, fitequation, 'k-')

        plt.xlabel(xname.translate(SUB))
        plt.ylabel(yname.translate(SUB))
        plt.title(f"{xname.translate(SUB)} vs {yname.translate(SUB)}" )

        eq = r"$\hat{y}$ = " + str(round(params[0],2)) + "x + " + str(round(params[1],4))
        plt.text(0.01, 1.15, eq, transform=plt.gca().transAxes, verticalalignment="top",
                bbox=dict(facecolor="white", alpha = 0.5))
        sl = "m = " + str(round(params[0],2)) + r" $\pm$ " + \
            str(round(sqrt(covmat[0,0]),2))
        plt.text(0.01, 1.06, sl, transform=plt.gca().transAxes, verticalalignment="top", 
                bbox=dict(facecolor="white", alpha = 0.5))
        interc = "b = " + str(round(params[1],4)) + r" $\pm$ " + \
            str(round(sqrt(covmat[1,1]),4))
        plt.text(0.35, 1.15, interc, transform=plt.gca().transAxes, verticalalignment="top", 
                bbox=dict(facecolor="white", alpha = 0.5))



        # Print the fit function equation, the uncertainties of the parameters,
        print("y = {0:3.2f} x + {1:6.4f}" . format(params[0], params[1]))
        print('m = {0:3.2f} +/- {1:3.2f}' . format(params[0], sqrt(covmat[0,0])))
        print('b = {0:6.4f} +/- {1:6.4f}' . format(params[1], sqrt(covmat[1,1])))
        # Calculate and print out the uncertainty of fit
        ufit = sqrt(sum((rifun())**2)/(len(y) - 2))
        print('Fit uncertainty = {0:4.3f}'.format(ufit))
        plt.text(0.71, 1.15, r"$\sigma_{\hat{y}} =$ " + str(round(ufit,2)), transform=plt.gca().transAxes,
            verticalalignment="top", bbox=dict(facecolor="white", alpha = 0.5))
        # Calculate and print out the coefficient of determination
        r2 = 1. -  sum((y - function(x, *params))**2)/sum((y - y.mean())**2)
        print (sum((y - function(x, *params))**2))
        print (sum((y - y.mean())**2))
        print("R^2 = {0:4.3f}". format(r2))
        plt.text(0.90, 1.15, r"$R^2$ = " + str(round(r2, 2)), transform=plt.gca().transAxes,
            verticalalignment="top", bbox=dict(facecolor="white", alpha = 0.5))
        # Calculate and print out the reduced chi-squared.
        rchi2 = sum((y - function(x, *params))**2/(ufit**2 + sigmaval**2))/(len(x) - len(params) - 1)
        print("Reduced chi-squared = {0:4.3f}".format(rchi2))
        plt.text(0.71, 1.06, r"$\chi^2/$dof = " + str(round(rchi2, 2)), transform=plt.gca().transAxes,
            verticalalignment="top", bbox=dict(facecolor="white", alpha = 0.5))
        
        if show_bool =="True" and save_bool == "True":
            plt.savefig(f"{filename_prefix}.png")
            plt.show()    
        elif show_bool == "True" and save_bool == "False":
            plt.show()
        elif show_bool == "False" and save_bool == "True":
            plt.savefig(f"{filename_prefix}.png")
        else:
            return rifun()
        plt.close(reggraph)
        return rifun()
    else:
        return rifun()
    

    
def histogramfunction(vals, yname, filename_prefix="Plot"):
    hisfig = plt.figure()
    plt.hist(vals, bins=12)
    plt.xlabel('Residual Vaules')
    plt.ylabel('Frequency')
    plt.title(f'{yname.translate(SUB)} Residual Distribution')
    plt.savefig(f"{filename_prefix}.png")
    close(hisfig)

def resScatterPlt(x, r, xname, rname, filename_prefix="Plot"):
    sctrplt = plt.figure()
    plt.scatter(x,r)
    plt.xlabel(xname.translate(SUB))
    plt.ylabel(rname.translate(SUB))
    plt.title(f"{xname.translate(SUB)} vs {rname.translate(SUB)}" )
    plt.savefig(f"{filename_prefix}.png")
    plt.close(sctrplt)
    

    
