import streamlit as st
import json
import pandas as pd
from streamlit_lottie import st_lottie
from PIL import Image
import numpy as np
import plotly.express as px
import pydeck as pdk


def config_page():
    st.set_page_config(page_title = "SUPERSTORE", page_icon=":chart:", layout="centered")

def home():
    st.title("Grupo SuperStore")

    st.subheader("Introducción")

    img = Image.open("data/foto oficina.jpg")
    st.image(img,use_column_width="auto")

    st.markdown("""SuperStore es el **grupo lider** en el sector de tecnología, suministros y equipamiento de oficina en Estados Unidos. 
    El grupo nació hace más de 30 años en Detroit (EEUU). \n Fue la primera empresa en desarrollar una plataforma B2B de compra online de materiales para el entorno de trabajo en 1999. Su catálogo incluye productos tecnológicos, suministros y equipamiento de oficina. 
    A fecha de hoy disponen de **más de 60.000 empresas clientes** en EEUU.""")

    with st.expander("Sostenibilidad"):
        st.markdown("""SuperStore garantiza que todos los pasos que da para satisfacer a sus clientes se realizan del modo 
                más sostenible posible.""")
        st.markdown("""
                * Más de la mitad de los productos son ecológicos. \n
                * El grupo ha reducido en una tercera parte sus emisiones de CO2 (desde 2010). \n
                * Asimismo, ha reducido al máximo los embalajes y optimizado sus rutas de transporte""")

def carga_datos(): 
    uploaded_file = st.file_uploader("Cargar CSV", type=["csv"])
    
    if uploaded_file is not None: 
        global dataset 
        dataset = pd.read_csv(uploaded_file, parse_dates=["Order Date"])
        dataset["Order Date Year"] = dataset["Order Date"].dt.strftime('%Y')
                
        if st.button("Ver datos"):
            st.markdown("<h3 style='text-align: center; color: red;'>DataFrame (2013 - 2016)</h3>", unsafe_allow_html=True)
            st.dataframe(dataset)
            pivot_table = pd.pivot_table(dataset, values="Sales", columns="Region", index="Order Date Year", aggfunc=np.sum).copy()
            st.markdown("<p style='text-align: center;'>Ventas totales por Estado (2013 - 2016)</p>", unsafe_allow_html=True)
            #st.markdown("<h3 style='text-align: center; color: red;'>Ventas totales por Estado (2013 - 2016)</h3>", unsafe_allow_html=True)
            st.line_chart(pivot_table)
            st.balloons()
            st.snow()
            with open("data/animation.json") as source:
                animation = json.load(source)
            st_lottie(animation, height=100, width=100)

def ventas_cat_tabla():

    #Tabla de ventas por categoría
    dataset_sales = pd.DataFrame(dataset.groupby("Category")["Sales"].sum())
    
    dataset_sales ["Percentage"] = ((dataset_sales ["Sales"] /dataset_sales ["Sales"].sum())*100).round(2)
    dataset_sales ["Percentage"] = dataset_sales ["Percentage"].astype(str) + " %"  
    dataset_sales ["Sales"] = dataset_sales ["Sales"].astype("int")
    
    st.table(dataset_sales)
    return dataset_sales

def ventas_cat_barplot():

    df_ventas_cat = dataset.groupby(["Order Date Year","Category"])["Sales"].sum().reset_index()
    
    # bar plot    
    fig1 = px.bar(df_ventas_cat, 
              x="Order Date Year",
              y = "Sales",
             color='Category',
             labels={"Order Date Year":''},
             color_discrete_sequence = px.colors.qualitative.Antique,
             height=500, 
             width=600)

    fig1.update_layout(font=dict(size=9),title_text="Ventas de artículos por categoría y año")

    return fig1

def ventas_subcat_barplot():

    dataset_subcat = dataset.groupby(["Order Date Year", "Category", "Sub-Category"])["Sales"].sum().reset_index()
    
    year = st.slider('Por favor, selecciona un año', 2013, 2016)
    
    if year == 2013:
        data = dataset_subcat[dataset_subcat["Order Date Year"] == "2013"]
    elif year == 2014:
        data = dataset_subcat[dataset_subcat["Order Date Year"] == "2014"]
    elif year == 2015:
        data = dataset_subcat[dataset_subcat["Order Date Year"] == "2015"]
    else:
        data = dataset_subcat[dataset_subcat["Order Date Year"] == "2016"]
    
    # bar plot

    fig2 = px.bar(data, 
              x="Sub-Category",
              y = "Sales",
             color='Category',
             template="plotly_white",
             labels={"Order Date Year":'',"Sub-Category":" "},
             color_discrete_sequence = px.colors.qualitative.Antique,
             height=500, 
             width=600,
             title = "Ventas por Sub-categoría año "+ str(year))

    fig2.update_layout(font=dict(size=20))

    return fig2


def ventas_subcat_lc():
    
    dataset_order_date_subcat = dataset.groupby(["Order Date Year", "Sub-Category"])["Sales"].sum().reset_index()
    
    year = st.slider('¿Qué años quieres seleccionar?', 2013, 2016,(2013, 2016))
    
    with st.sidebar:
        sub_category = st.multiselect('Escoge la Sub-Categoría', ['Paper', 'Labels', 'Storage', 'Binders', 'Art', 'Chairs', 'Phones',
       'Fasteners', 'Furnishings', 'Accessories', 'Envelopes',
       'Bookcases', 'Appliances', 'Tables', 'Supplies', 'Machines',
       'Copiers'], ['Paper', 'Labels', 'Storage', 'Binders', 'Art', 'Chairs', 'Phones',
       'Fasteners', 'Furnishings', 'Accessories', 'Envelopes',
       'Bookcases', 'Appliances', 'Tables', 'Supplies', 'Machines',
       'Copiers'])
    
    #line chart
    list_columns = []
    if year[0] != year[1]:
        if sub_category != []:
            
            for i in range(len(sub_category)):
                list_columns.append(sub_category[i])
                
            st.subheader("Ventas Sub-Categoría por año")
            df_sub_categ_mask = dataset_order_date_subcat[dataset_order_date_subcat["Sub-Category"].isin(list_columns)]
                        
            fig3 = px.line(df_sub_categ_mask[df_sub_categ_mask["Order Date Year"].isin([str(x) for x in np.arange(year[0], year[1] + 1)])],
                           x = "Order Date Year",
                           y = "Sales",
                           color= "Sub-Category",
                           labels={"Order Date Year":'',"Sub-Category":" "},
                           title='Ventas Sub-Categoría',
                           height=700, 
                            width=700,
                            markers=True
            )
            return fig3
        else: 
            return 2
    else:
        return 1 
    

def ventas_estado():
    df_cities = pd.read_csv("data/statelatlong.csv")
    dataset2 = dataset.copy()
    dataset2["Order Date Year"] = dataset2["Order Date"].dt.year
    df_map = dataset2.groupby(["State", "Order Date Year"])[["Sales"]].sum().reset_index().merge(df_cities, left_on="State", right_on="City").drop(columns=["State_y", "City"]).rename(columns={"State_x":"State"})

    years =[2013, 2014, 2015, 2016]
    sell_year = st.selectbox('Escoge el año', years)
    if sell_year in years:   
        year_to_show = sell_year
    
    view = pdk.ViewState(latitude=37, longitude=-95, zoom=3,)
    
    tooltip = {
        "html":
            "<b>Estado:</b> {State} <br/>"
            "<b>Ventas:</b> {Sales} <br/>",
        "style": {
            "backgroundColor": "steelblue",
            "color": "black",
        }
    }
    salesLayer = pdk.Layer(
            type= "ScatterplotLayer",
            data=df_map,
            pickable=True,
            opacity=0.3,
            filled=True,
            onClick=True,
            radius_scale=10,
            radius_min_pixels=0,
            radius_max_pixels=30,
            line_width_min_pixels=1,
            get_position=["Longitude", "Latitude"],
            get_radius="Sales",
            get_fill_color=[252, 136, 3],
            get_line_color=[255,0,0],
        )

    r = pdk.Deck(
        layers=[salesLayer],
        initial_view_state=view,
        map_style="mapbox://styles/mapbox/light-v10",
        tooltip=tooltip,
    )
    map = st.pydeck_chart(r)
    salesLayer.data = df_map[df_map['Order Date Year'] == year_to_show]
  
    r.update()
    map.pydeck_chart(r)