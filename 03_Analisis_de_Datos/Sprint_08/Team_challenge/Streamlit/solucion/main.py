import streamlit as st
import functions as ft



## Basic setup and app layout

ft.config_page()

menu = st.sidebar.selectbox("Elige una sección",("Panorámica",  "Carga tus datos","Analiza las ventas"))

if menu == "Panorámica": 
    ft.home()

elif menu == "Carga tus datos":
    ft.carga_datos()

else:
    menu_ventas = st.sidebar.radio("Escoge lo que te interesa analizar",options=["Ventas por categoría", "Ventas por subcategoría", "Ventas por Estado"])

    if menu_ventas == "Ventas por categoría":

        st.header("Ventas por categoría")

        table = ft.ventas_cat_tabla()

        fig1 = ft.ventas_cat_barplot()

        st.plotly_chart(fig1, use_container_width=True)

    elif menu_ventas == "Ventas por subcategoría":

        st.header("Ventas por subcategoría de producto")

        fig2 = ft.ventas_subcat_barplot()

        st.plotly_chart(fig2,use_container_width=True)

        fig3 = ft.ventas_subcat_lc()
        
        if fig3 == 1:
           st.write("Seleccione un rango de años a filtrar")
        elif fig3 == 2:
            st.write("Seleccione la(s) categoria(s) a filtrar")
        else:
            st.plotly_chart(fig3,use_container_width=True)

    else:
        ft.ventas_estado()