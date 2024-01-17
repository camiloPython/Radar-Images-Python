# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 07:29:09 2022

@author: Roberto Camilo Vindas (rvindas/DMSA/IMN) 


Script de python para graficar datos de radar (reflectividad y velocidad radial) usando datos netcdf del radar banda x del IMN.
El radar es un modelo Ranger X-Band de la empresa Enterprise Electronics Corporation (ECC)

Este script fue probado existosamente con las siguientes versiones de la librerias:
cartopy 0.21.1
matplotlib 3.8.0
numpy 1.26.2
netCDF4 1.6.2
pillow 10.0.1
"""


import cartopy
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import netCDF4
import glob
import datetime
from  PIL import Image
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import sys



def preparaTitulos(variable, archivo):
    
    """
    Funcion que prepara los titulos del grafico y el nombre del mismo a partir del 
    nombre del archivo que tiene un formato definido, ej. 20220902-233911.nc
    
    Recibe:
        variable(str): Un string que indica el tipo de variable a graficar.
        
                      "DBZV" para Reflectividad polarización Vertical 
                      "DBZH" para Reflectividad polarización Horizontal 
                      "VELH" para Velocidad Radial polarización Horizontal
                      "VELV" para Velocidad Radial polarización Vertical
                 
                      
    Regresa:
        Una tupla de dos entradas con (en orden):
            titulo(str): Titulo para poner en el grafico 
            nombreGrafico(str): Nombre para guardar el grafico (sin la ruta)
    
    """
    
    
    
    diccVariables = {"DBZV": "Reflectividad Vertical", "DBZH": "Reflectividad Horizontal", 
                     "VELH":"Velocidad Radial(H)","VELV":"Velocidad Radial(V)"}
    
    
    nombreArchivo = archivo.split("\\")[-1]
    anno = int(nombreArchivo[0:4])
    mes = int(nombreArchivo[4:6])
    dia = int(nombreArchivo[6:8])  
    hora = int(nombreArchivo[9:11])
    minutos = int(nombreArchivo[11:13])
    segundos = int(nombreArchivo[13:15])
    
    #La hora en Costa Rica es UTC-6 
    hoy = datetime.datetime(anno, mes, dia, hora, minutos, segundos) + datetime.timedelta(hours = -6)
    
    if hoy.day < 10:
        dia = "0%d"%(hoy.day)
    else:
        dia = str(hoy.day)
        
    if hoy.month < 10:
       mes = "0%d"%(hoy.month)
    else:
       mes = str(hoy.month)
    
    if hoy.minute < 10:
       minutos = "0%d"%(hoy.minute)
    else:
       minutos = str(hoy.minute)
    if hoy.second < 10:
        segundos = "0%d"%(hoy.second)
    else:
        segundos = str(hoy.second)
    if hoy.hour < 10:
        hora = "0%d"%(hoy.hour)
    else:
        hora = str(hoy.hour)    
    
    anno = str(hoy.year)
    
    titulo = "IMN-Radar %s %s/%s/%s %s:%s:%s (Local)"%(diccVariables[variable], anno,mes,dia,hora,minutos,segundos)
    nombreGrafico = variable + "_" + "%s%s%s-%s%s%s.png"%(anno,mes,dia,hora,minutos,segundos)
    
    return (titulo, nombreGrafico)
    

    


def graficaRadar(archivoRadar, variable, ciudades, nombreGrafico, titulo, carpetaGuardarGrafico,logo, xLogo, yLogo, dominio, zoomLogo,fraccion, reducido = False):
    
    """
    Funcion para graficar las variables del radar sobre un mapa de Costa Rica.
    
    Recibe:
        archivoRadar(str): La ruta con el archivo netcdf con los datos del radar 
        
        variable(str): variable(str): Un string que indica el tipo de variable a graficar.
                      "DBZV" para Reflectividad polarización Vertical 
                      "DBZH" para Reflectividad polarización Horizontal 
                      "VELH" para Velocidad Radial polarización Horizontal
                      "VELV" para Velocidad Radial polarización Vertical
        
        ciudades(dict): Un diccionario con cada llave el nombre de un ciudad y cada valor una lista con la longitud (entrada 0) y la latitud
                        (entrada 1) de la ciudad
        
        nombreGrafico(str): El nombre con el que se va a guardar la imagen  
        
        titulo(str): El titulo para poner en la parte de arriba del grafico 
        
        carpetaGuardarGrafico(str): la ruta de la carpeta en donde se va a guardar el gráfico
        
        logo(str): la ruta donde está la imagen con el logo institucional a colocar en la imagen final.
        
        xLogo(int): Coordenada en x para colocar el logo en la imagen final. Esto depende del tamaño de la imagen o dominio geografico.
            
        yLogo(int): Coordenada en y para colocar el logo en la imagen final. Esto depende del tamaño de la imagen o dominio geografico.
        
        dominio(list): Una lista con las coordenadas geograficas (coordenadas decimales) que delimitan el área del gráfico. las primeras dos entradas
                       corresponden a la longitud y las ultimas dos a la latitud.
        
        zoomLogo(float): Valor para el zoom al logo. Esto depende del tamaña del grafico
        
        fraccion(float): Valor que indica la fracción de los ejes original a usar en el tamaño de la barra de color 
        
        reducido(bool): Booleano que indica si el grafico a realizar es enfocado en el Valle Central o se toma todo Costa Rica
        
    Regresa: None   
    
    """
    

    datos = netCDF4.Dataset(archivoRadar)
    radlat =  datos.variables["latitude"][:].data
    radlon = datos.variables["longitude"][:].data
    rango = datos.variables["range"][:].data
    azimuth = datos.variables["azimuth"][:].data
    campo = datos[variable][:].data
    datos.close()
    
    x = rango * np.sin(np.deg2rad(azimuth))[:,None]
    y = rango * np.cos(np.deg2rad(azimuth))[:,None]

    proj=cartopy.crs.LambertConformal(central_longitude=radlon, central_latitude=radlat)
    fig = plt.figure(figsize=(20,20))
    ax = plt.subplot(1,1,1,projection = proj)
    proyeccion = cartopy.crs.PlateCarree()
    ax.set_extent(dominio, proyeccion)
    ax.set_facecolor(cartopy.feature.COLORS['water'])
    ax.add_feature(cartopy.feature.LAND)
    ax.add_feature(cartopy.feature.COASTLINE)
    #ax.add_feature(cartopy.feature.LAKES, alpha=0.5)
    ax.set_title(titulo, fontsize=22, fontweight=0, color='purple', loc='center', style='italic')
    ax.add_feature(cartopy.feature.BORDERS, linewidth=1, edgecolor='green', linestyle='--')
    ax.add_feature(cartopy.feature.STATES, linewidth=0.3, edgecolor='black')
    #ax.add_feature(cartopy.feature.RIVERS, linewidth=0.3, edgecolor='blue')
   
    #Circulos de varios radios
    marcadoresCirculo = {"30km":[10.05456,-83.82269],"60km":[10.17530, -83.57759],"120km":[10.470731082600837, -83.11855002599704]}
    for marcador in marcadoresCirculo.keys():
        lon = marcadoresCirculo[marcador][1]
        lat = marcadoresCirculo[marcador][0]
        ax.text(lon + 0.01, lat + 0.01, marcador, fontsize=15, color = "black",transform=proyeccion)
    circulo = plt.Circle((radlat, radlon), radius=33700, fill = False)
    ax.add_artist(circulo)
    circulo2 = plt.Circle((radlat, radlon), radius=67200, fill = False)
    ax.add_artist(circulo2)
    circulo3 = plt.Circle((radlat, radlon), radius=134100, fill = False)
    ax.add_artist(circulo3)
    
    
    for ciudad in ciudades.keys():
        lon = ciudades[ciudad][1]
        lat = ciudades[ciudad][0]
        ax.plot(lon, lat, "k*", markersize=2,zorder=1, transform=proyeccion)
        ax.text(lon + 0.01, lat + 0.01, ciudad, fontsize=10, color = "purple",transform=proyeccion)

    print("variable> ", variable)
    if variable == "VELH" or variable == "VELV":
        cmap=plt.cm.get_cmap('coolwarm')
        norm = mpl.colors.Normalize(vmin=-8, vmax=8)
        campo = np.ma.masked_array(campo, campo < -8) 
        etiqueta = "m/s"
    elif variable == "DBZV" or variable == "DBZH":       
        cmap=plt.cm.get_cmap('tab20c')
        norm = mpl.colors.Normalize(vmin=0, vmax=100)
        campo = np.ma.masked_array(campo, campo < 0) 
        etiqueta = "dBz"

    mesh = ax.pcolormesh(x,y,campo, zorder = 0, norm = norm, cmap = cmap)
    plt.colorbar(mesh, orientation='vertical',fraction=fraccion, label = etiqueta)
     
    img = Image.open(logo)
    imagebox = OffsetImage(img, zoom=zoomLogo)
    imagebox.image.axes = ax
    ab = AnnotationBbox(imagebox, [xLogo, yLogo], xycoords='data', frameon=True)
    ax.add_artist(ab)
    
    if reducido:
        plt.savefig(carpetaGuardarGrafico + "%s_actualRed.png"%(variable),bbox_inches='tight')
    else:
        plt.savefig(carpetaGuardarGrafico + "%s_actual.png"%(variable),bbox_inches='tight')
        









###########################################################################################################################################################################
########################### CORRIDA DEL PROGRAMA ##########################################################################################################################
###########################################################################################################################################################################


carpetaRadar = "datos\\"
logo = "imn.jpg"
carpetaGuardarGrafico = "imagenesTest\\"
nombreArchivos = ["Reflectividad", "viento"]
variables = ["VELH","DBZV","DBZH","VELV"]


listaRealArchivos = []
for archivo in glob.iglob(carpetaRadar + "*.nc"):
    for llave in nombreArchivos:
        if archivo.find(llave) != -1:
            listaRealArchivos.append(archivo)


#En principio no sabemos si el archivo tiene datos polarizados vertical u horizontal.
try:
    archivosDatos = {}
    for archivo in listaRealArchivos:
        print (archivo)         
        data = netCDF4.Dataset(archivo)
        datos = data.variables.keys()
        data.close()
        for variable in variables:
            #Averiguar que tipo de polarización tiene la variable
            print ("hello: ", variable)
            if variable in datos:
                archivosDatos.setdefault(variable, archivo)


    for variable in archivosDatos.keys():
        archivo = archivosDatos[variable]
        print("Corriendo el programa .....")


        ciudades = {"Liberia" : [10.6350403, -85.4377213],"Golfito": [8.6032696,-83.1134186], "San Jose": [9.9333296, -84.0833282], "Alajuela": [10.0162497, -84.2116318], 
            "Cd. Quesada":[10.3238096, -84.4271393], "Cartago":[9.86444, -83.9194412], "Siquirres":[10.0974798, -83.5065918], "San Vito": [8.8207903, -82.9709167], 
            "Upala":[10.899065, -85.017947], "Los Chiles":[11.03333,-84.7166672],"Sarapiquí":[10.452225, -84.018191], "Palmares":[10.060881, -84.43], 
            "Limon": [9.9907398, -83.0359573], "Quepos": [9.4306297, -84.1623077],"Nosara":[9.979184, -85.649843]}



        dominio = [-86, -82.6, 8, 11.3]
        xLogo = -160000
        yLogo = -190000
        zoomLogo = 1.2
        fraccion=0.04

    
        archivoRadar = archivo 
        titulo, nombreGrafico = preparaTitulos(variable, archivo)

        print ("Graficando radar ....")

        graficaRadar(archivoRadar, variable, ciudades, nombreGrafico, titulo, carpetaGuardarGrafico, logo, xLogo, yLogo, dominio, zoomLogo,fraccion)



################################################################################################################
###########################################dominio mas pequeno##################################################
################################################################################################################
        dominio = [-85, -83.2, 9.3, 10.8]
        xLogo = -100000
        yLogo = -70000
        zoomLogo = 0.35
        fraccion=0.035
        ciudades = { "San José": [9.9333296, -84.0833282], "Paquera": [9.82139, -84.9383], "Puntarenas": [9.9762497, -84.8383636],"Alajuela": [10.0162497, -84.2116318], 
           "Cd. Quesada":[10.3238096, -84.4271393], "Cartago":[9.86444, -83.9194412], "Siquirres":[10.0974798, -83.5065918], "Naranjo":[10.097380, -84.379059], 
            "Sarapiquí":[10.452225, -84.018191], "Palmares":[10.060881, -84.43],"Heredia": [9.998289, -84.121291],"Santa Bárbara": [10.037220, -84.158898], 
             "Quepos": [9.4306297, -84.1623077], "Turrialba":[ 9.908138, -83.679943], "Jacó":[9.611920, -84.627986], "Desamparados":[9.896291, -84.063445],
             "Tortuguero":[10.541779, -83.502059], "Guápiles":[10.215029, -83.789012], "Pérez Zeledón":[9.373451, -83.702680], "Purral":[9.962138, -84.007336],
             "Orotina":[9.909615, -84.523841], "Salitrales":[9.766057, -84.400014], "Tarbaca":[9.811155, -84.118058], "Paraíso":[9.838339, -83.866003], 
             "Tierra Blanca": [9.915681, -83.892272], "Cd. Colón":[9.913613, -84.242011], "Puriscal": [9.847338, -84.314607],"San Marcos":[9.659382,-84.021852],
             "Pital":[10.452861, -84.277412]}

        graficaRadar(archivoRadar, variable, ciudades, nombreGrafico, titulo, carpetaGuardarGrafico, logo, xLogo, yLogo, dominio, zoomLogo, fraccion, reducido=True)
   

except Exception as e:
    e_type, e_object, e_traceback = sys.exc_info()
    e_line_number = e_traceback.tb_lineno
    print ("Ocurio la excepción: ", e)
    print ("Tipo: ", e_type)
    print ("En la linea ", e_line_number)


